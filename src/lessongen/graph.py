"""The generate -> evaluate -> regenerate loop as a LangGraph state machine.

generate -> deterministic -> (fail) -> log_rejection -> generate ...   (bounded by max_retries)
                          -> (pass) -> judge -> (fail) -> log_rejection
                                            -> (pass) -> finalize -> reflect -> END
log_rejection -> finalize once retries are exhausted (best attempt, flagged needs_human_review)
"""
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, StateGraph

from . import generator, inject, logbook
from .config import ROOT, path_of
from .evaluator.deterministic import run_deterministic
from .evaluator.judge import run_judge
from .evaluator.rubric import load_rubric
from .llm import LLM
from .reflector import reflect


class RunState(TypedDict, total=False):
    judged: bool
    topic: str
    attempt: int
    max_retries: int
    lesson: str
    verdicts: list
    det_ok: bool
    all_ok: bool
    feedback: str
    history: list
    rejection_log: list
    memory_lessons: list
    inject: str
    status: str
    final_lesson: str
    best_attempt: int
    memory_update: dict


@dataclass
class Ctx:
    cfg: dict
    llm: LLM
    store: object
    checks: list
    facts: str
    prompts: dict
    run_dir: Path
    run_id: str


def _fails(verdicts):
    return [v for v in verdicts if not v["passed"]]


def build_graph(ctx: Ctx):
    def n_generate(s: RunState):
        attempt = s.get("attempt", 0) + 1
        lesson = generator.generate(ctx.llm, ctx.prompts["generator"], s["topic"], ctx.facts, s["memory_lessons"], attempt, bool(s.get("inject")), s.get("lesson"), s.get("feedback"))
        injected = None
        if s.get("inject") and attempt == 1:
            lesson, injected = inject.apply(s["inject"], lesson), s["inject"]
        rej = [dict(e) for e in s.get("rejection_log", [])]
        if attempt > 1 and rej:
            rej[-1]["changes_made"] = logbook.diff_summary(s["lesson"], lesson)
        logbook.write_attempt(ctx.run_dir, attempt, lesson)
        return {"attempt": attempt, "lesson": lesson, "rejection_log": rej, "history": s.get("history", []) + [{"attempt": attempt, "lesson": lesson, "injected": injected, "verdicts": []}]}

    def n_deterministic(s: RunState):
        v = [x.model_dump() for x in run_deterministic(s["lesson"], ctx.checks, ctx.cfg)]
        hist = [dict(h) for h in s["history"]]
        hist[-1]["verdicts"] = v
        return {"verdicts": v, "det_ok": not _fails(v), "judged": False, "history": hist}

    def n_judge(s: RunState):
        v = s["verdicts"] + [x.model_dump() for x in run_judge(ctx.llm, ctx.checks, s["lesson"], ctx.facts, ctx.prompts["judge"])]
        hist = [dict(h) for h in s["history"]]
        hist[-1]["verdicts"] = v
        return {"verdicts": v, "all_ok": not _fails(v), "judged": True, "history": hist}
    
    def n_log_rejection(s: RunState):
        failed = _fails(s["verdicts"])
        skipped = not s["det_ok"] and not s.get("judged")
        rej = [dict(e) for e in s.get("rejection_log", [])]
        if s["attempt"] > 1 and rej:
            logbook.update_outcome(rej[-1], s["verdicts"])
        feedback = generator.format_feedback(failed, skipped)
        rej.append({
            "attempt": s["attempt"],
            "failed": [{"check_id": v["check_id"], "reason": v["reason"], "evidence": v["evidence"]} for v in failed],
            "skipped_llm_judge": skipped,
            "feedback_sent": feedback,
            "changes_made": "",
            "outcome_next_attempt": {},
        })
        return {"rejection_log": rej, "feedback": feedback, "all_ok": False}

    def n_finalize(s: RunState):
        rej = [dict(e) for e in s.get("rejection_log", [])]
        if s.get("all_ok"):
            if s["attempt"] > 1 and rej:
                logbook.update_outcome(rej[-1], s["verdicts"])
            return {"status": "passed", "final_lesson": s["lesson"], "best_attempt": s["attempt"], "rejection_log": rej}
        best = min(s["history"], key=lambda h: (len(_fails(h["verdicts"])), -h["attempt"]))
        return {"status": "needs_human_review", "final_lesson": best["lesson"], "best_attempt": best["attempt"], "rejection_log": rej}

    def n_reflect(s: RunState):
        update = reflect(ctx.cfg, ctx.llm, ctx.store, ctx.checks, s, ctx.run_id, ctx.prompts["reflector"])
        ctx.store.record_run(ctx.run_id, s["topic"], s["status"], s["attempt"], ctx.llm.tokens)
        new = {**s, "memory_update": update}
        logbook.write_all(ctx.run_dir, new, {"llm_calls": ctx.llm.calls, "cache_hits": ctx.llm.cache_hits, "tokens": ctx.llm.tokens})
        return {"memory_update": update}

    g = StateGraph(RunState)
    for name, fn in [("generate", n_generate), ("deterministic", n_deterministic), ("judge", n_judge), ("log_rejection", n_log_rejection), ("finalize", n_finalize), ("reflect", n_reflect)]:
        g.add_node(name, fn)
    g.set_entry_point("generate")
    g.add_edge("generate", "deterministic")
    g.add_conditional_edges("deterministic", lambda s: "judge" if (s["det_ok"] or (s.get("inject") == "false_claim" and s["attempt"] == 1)) else "log_rejection", {"judge": "judge", "log_rejection": "log_rejection"})
    g.add_conditional_edges("judge", lambda s: "finalize" if s["all_ok"] else "log_rejection", {"finalize": "finalize", "log_rejection": "log_rejection"})
    g.add_conditional_edges("log_rejection", lambda s: "generate" if s["attempt"] < s["max_retries"] + 1 else "finalize", {"generate": "generate", "finalize": "finalize"})
    g.add_edge("finalize", "reflect")
    g.add_edge("reflect", END)
    return g.compile()


def run_pipeline(cfg: dict, llm: LLM, store, topic: str, inject_fault: str | None = None, max_retries: int | None = None) -> tuple[RunState, Path]:
    run_id = ("mock-" if llm.mock else "") + time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time() * 1000) % 1000:03d}"
    ctx = Ctx(
        cfg=cfg, llm=llm, store=store, checks=load_rubric(store),
        facts=(ROOT / "data" / "facts.md").read_text(encoding="utf-8"),
        prompts={k: (ROOT / "prompts" / f"{k}.md").read_text(encoding="utf-8") for k in ("generator", "judge", "reflector")},
        run_dir=path_of(cfg, "runs_dir") / run_id, run_id=run_id,
    )
    lessons = store.active_lessons()
    store.bump_hits([l["id"] for l in lessons])
    init: RunState = {
        "topic": topic, "attempt": 0, "max_retries": cfg["max_retries"] if max_retries is None else max_retries,
        "memory_lessons": [l["text"] for l in lessons], "history": [], "rejection_log": [], "inject": inject_fault or "",
    }
    final = build_graph(ctx).invoke(init, {"recursion_limit": 60})
    return final, ctx.run_dir
