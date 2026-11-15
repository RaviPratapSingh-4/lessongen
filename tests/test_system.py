import copy

import pytest

from lessongen import inject
from lessongen.config import ROOT, load_config
from lessongen.evaluator.deterministic import run_deterministic
from lessongen.evaluator.judge import run_judge
from lessongen.evaluator.rubric import load_rubric
from lessongen.graph import run_pipeline
from lessongen.llm import LLM, LLMResponse
from lessongen.memory.sqlite_store import SQLiteStore

GOOD = (ROOT / "tests/fixtures/good.md").read_text(encoding="utf-8")


@pytest.fixture
def env(tmp_path):
    cfg = load_config()
    cfg = copy.deepcopy(cfg)
    cfg["paths"].update(runs_dir=str(tmp_path / "runs"), cache_dir=str(tmp_path / "cache"))
    return cfg, SQLiteStore(tmp_path / "m.db")


def test_good_passes_all_deterministic():
    cfg = load_config()
    assert all(v.passed for v in run_deterministic(GOOD, load_rubric(), cfg))


@pytest.mark.parametrize("name", [n for n in inject.VARIANTS if n != "false_claim"])
def test_each_defect_caught(name):
    cfg = load_config()
    failed = {v.check_id for v in run_deterministic(inject.apply(name, GOOD), load_rubric(), cfg) if not v.passed}
    assert set(inject.VARIANTS[name][1]) <= failed


class Stub(LLM):
    """LLM stub returning scripted text per role."""

    def __init__(self, cfg, replies):
        super().__init__(cfg, mock=True)
        self.replies = replies

    def chat(self, role, system, user, json_mode=False, meta=None):
        self.calls += 1
        r = self.replies[role]
        return LLMResponse(r(meta or {}) if callable(r) else r)


def test_judge_fails_closed_on_garbage(env):
    cfg, _ = env
    v = run_judge(Stub(cfg, {"judge": "not json at all"}), load_rubric(), GOOD, "facts", "<<CHECKS>><<LESSON>><<IDS>><<FACTS>>")
    assert v and not any(x.passed for x in v)


def test_judge_rejects_fake_evidence(env):
    cfg, _ = env
    import json

    fake = json.dumps({"verdicts": [{"check_id": c.id, "passed": True, "evidence": "this sentence is not in the lesson", "reason": "", "fix": ""} for c in load_rubric() if c.type == "llm"]})
    v = run_judge(Stub(cfg, {"judge": fake}), load_rubric(), GOOD, "facts", "<<CHECKS>><<LESSON>><<IDS>><<FACTS>>")
    assert not any(x.passed for x in v) and "Unverified" in v[0].reason


def test_loop_recovers_and_logs(env):
    cfg, store = env
    final, run_dir = run_pipeline(cfg, LLM(cfg, mock=True), store, "RAG")
    assert final["status"] == "passed" and final["attempt"] == 2
    e = final["rejection_log"][0]
    assert {f["check_id"] for f in e["failed"]} == {"D3", "D4"} and e["skipped_llm_judge"]
    assert e["changes_made"] and "D4" in e["outcome_next_attempt"]["resolved"]
    assert (run_dir / "rejection_log.md").exists() and (run_dir / "final_lesson.md").exists()


def test_injected_fault_caught_by_judge(env):
    cfg, store = env
    final, _ = run_pipeline(cfg, LLM(cfg, mock=True), store, "RAG", inject_fault="false_claim")
    assert final["rejection_log"][0]["failed"][0]["check_id"] in ("L1", "L2") and final["status"] == "passed"
    assert store.failure_counts() == {}  # deliberate faults are never learned from


def test_retries_exhausted_is_flagged_not_shipped(env):
    cfg, store = env
    bad = inject.too_short(GOOD)
    llm = Stub(cfg, {"generator": bad, "judge": "{}", "reflector": '{"lessons":[],"rubric_proposals":[]}'})
    final, _ = run_pipeline(cfg, llm, store, "RAG")
    assert final["status"] == "needs_human_review" and final["attempt"] == cfg["max_retries"] + 1
    assert len(final["rejection_log"]) == cfg["max_retries"] + 1


def test_memory_learns_after_repeated_failure_and_proposal_is_gated(env):
    cfg, store = env
    run_pipeline(cfg, LLM(cfg, mock=True), store, "RAG")      # D3,D4 fail once each -> below threshold
    assert store.active_lessons() == []
    run_pipeline(cfg, LLM(cfg, mock=True), store, "RAG")      # second occurrence -> lessons learned
    assert {l["check_id"] for l in store.active_lessons()} == {"D3", "D4"}
    final, _ = run_pipeline(cfg, LLM(cfg, mock=True), store, "RAG")
    assert len(final["memory_lessons"]) == 2                  # lessons are fed to the generator on the next run
    # rubric evolution is human-gated
    store.add_proposal("The lesson never claims RAG retrains the model.", "Remove it.", "x")
    assert not any(c.id.startswith("X") for c in load_rubric(store))
    pid = store.proposals()[0]["id"]
    store.set_proposal(pid, "approved")
    assert any(c.id == f"X{pid}" for c in load_rubric(store))
