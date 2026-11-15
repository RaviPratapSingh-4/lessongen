import argparse
import logging
import sys

from dotenv import load_dotenv

from . import inject
from .config import ROOT, load_config, path_of
from .evaluator.deterministic import run_deterministic
from .evaluator.judge import run_judge
from .evaluator.rubric import load_rubric
from .graph import run_pipeline
from .llm import LLM
from .memory.sqlite_store import SQLiteStore


def _store(cfg, mock):
    return SQLiteStore(path_of(cfg, "db_mock" if mock else "db"))


def cmd_run(a):
    cfg = load_config()
    llm, store = LLM(cfg, mock=a.mock, use_cache=not a.no_cache), _store(cfg, a.mock)
    final, run_dir = run_pipeline(cfg, llm, store, a.topic, a.inject, a.max_retries)
    print(f"\nTopic: {final['topic']}  |  status: {final['status'].upper()}  |  attempts: {final['attempt']}  |  run: {run_dir}")
    if final["memory_lessons"]:
        print(f"Memory lessons applied: {len(final['memory_lessons'])}")
    for h in final["history"]:
        bad = [v["check_id"] for v in h["verdicts"] if not v["passed"]]
        print(f"  attempt {h['attempt']}{' (injected: ' + h['injected'] + ')' if h['injected'] else ''}: {'PASS' if not bad else 'REJECTED ' + ', '.join(bad)}")
    mu = final.get("memory_update", {})
    for l in mu.get("new_lessons", []):
        print(f"  learned [{l['check_id']}]: {l['text']}")
    for p in mu.get("new_proposals", []):
        print(f"  rubric proposal #{p['id']} (pending your approval): {p['description']}")
    print(f"LLM calls: {llm.calls}  cache hits: {llm.cache_hits}  tokens: {llm.tokens}")


def cmd_memory(a):
    cfg = load_config()
    s = _store(cfg, a.mock)
    print("LESSONS (injected into generator prompt):")
    for l in s.active_lessons(50):
        print(f"  [{l['check_id']}] {l['text']}  (used in {l['hits']} runs)")
    print("FAILURE COUNTS:", s.failure_counts() or "none")
    print("PENDING RUBRIC PROPOSALS:")
    for p in s.proposals("pending"):
        print(f"  #{p['id']} {p['description']}")
    print("RECENT RUNS:")
    for r in s.runs():
        print(f"  {r['id']}  {r['status']}  attempts={r['attempts']}  tokens={r['tokens']}")


def cmd_rubric(a):
    cfg = load_config()
    s = _store(cfg, a.mock)
    if a.action == "review":
        for p in s.proposals("pending"):
            print(f"#{p['id']}  {p['description']}\n     fix hint: {p['fix_hint']}")
        print("Approve with: lessongen rubric approve <id>")
    else:
        ok = s.set_proposal(a.id, "approved" if a.action == "approve" else "rejected")
        print(("Done. " if ok else "No such proposal. ") + ("Approved checks become X<id> in the rubric." if a.action == "approve" else ""))


def cmd_eval(a):
    """Evaluator self-test: does it accept a good lesson and reject each planted defect?"""
    cfg = load_config()
    checks = load_rubric()
    good = (ROOT / "tests" / "fixtures" / "good.md").read_text(encoding="utf-8")
    llm = LLM(cfg, mock=a.mock) if a.llm else None
    facts = (ROOT / "data" / "facts.md").read_text(encoding="utf-8")
    tpl = (ROOT / "prompts" / "judge.md").read_text(encoding="utf-8")
    cases = [("good", good, [])] + [(n, f(good), exp) for n, (f, exp) in inject.VARIANTS.items()]
    wrong = 0
    for name, text, expected in cases:
        v = run_deterministic(text, checks, cfg)
        if llm and name in ("good", "false_claim"):
            v += run_judge(llm, checks, text, facts, tpl)
        failed = [x.check_id for x in v if not x.passed]
        ran = {x.check_id for x in v}
        ok = (not failed) if name == "good" else all(c in failed for c in expected if c in ran) and bool(failed)
        wrong += not ok
        print(f"{'OK ' if ok else 'BAD'} {name:14} failed={failed or 'none'}")
        for x in v:
            if not x.passed and x.source == "llm":
                print(f"      {x.check_id}: {x.reason} | evidence: {x.evidence[:120]}")
    sys.exit(1 if wrong else 0)


def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(prog="lessongen", description="Self-evaluating lesson generator")
    p.add_argument("--mock", action="store_true", help="use the offline mock LLM (no API calls)")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--mock", action="store_true", default=argparse.SUPPRESS)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", parents=[common], help="generate -> evaluate -> regenerate")
    r.add_argument("--topic", default="Introduction to RAG (Retrieval-Augmented Generation)")
    r.add_argument("--inject", choices=list(inject.VARIANTS), help="plant a deliberate defect in attempt 1")
    r.add_argument("--max-retries", type=int)
    r.add_argument("--no-cache", action="store_true")
    r.set_defaults(fn=cmd_run)
    sub.add_parser("memory", parents=[common], help="show learned lessons, failure counts, proposals").set_defaults(fn=cmd_memory)
    rb = sub.add_parser("rubric", parents=[common], help="review/approve/reject rubric proposals")
    rb.add_argument("action", choices=["review", "approve", "reject"])
    rb.add_argument("id", nargs="?", type=int)
    rb.set_defaults(fn=cmd_rubric)
    e = sub.add_parser("eval-fixtures", parents=[common], help="test the evaluator on good vs deliberately broken lessons")
    e.add_argument("--llm", action="store_true", help="also run the LLM judge on good + false_claim (uses a few API calls)")
    e.set_defaults(fn=cmd_eval)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
