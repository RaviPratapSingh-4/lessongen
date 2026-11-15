"""Run artifacts: attempt drafts, rejection log (JSON + readable Markdown), final lesson, run summary."""
import difflib
import json
from pathlib import Path

from .evaluator.deterministic import sentences, strip_md, words


def _sents(t):
    return sentences(strip_md(t))


def diff_summary(old: str, new: str) -> str:
    a, b = _sents(old), _sents(new)
    sm = difflib.SequenceMatcher(None, a, b)
    removed = added = 0
    new_s = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            removed += i2 - i1
        if tag in ("replace", "insert"):
            added += j2 - j1
            new_s += b[j1:j2]
    ex = "; e.g. now: " + " | ".join(f'"{s[:110]}"' for s in new_s[:2]) if new_s else ""
    return f"{len(words(strip_md(old)))}→{len(words(strip_md(new)))} words; {removed} sentence(s) removed/replaced, {added} added/rewritten{ex}"


def update_outcome(entry: dict, verdicts: list[dict]):
    """After the next attempt is evaluated, record which earlier failures were fixed."""
    now = {v["check_id"]: v["passed"] for v in verdicts}
    prev = [f["check_id"] for f in entry["failed"]]
    entry["outcome_next_attempt"] = {
        "resolved": [c for c in prev if now.get(c) is True],
        "still_failing": [c for c in prev if now.get(c) is False],
        "not_evaluated_yet": [c for c in prev if c not in now],
    }


def render_md(state: dict) -> str:
    out = [f"# Rejection log: {state['topic']}", "", f"Final status: **{state['status']}** after {state['attempt']} attempt(s).", ""]
    if not state["rejection_log"]:
        out.append("No attempt was rejected: the first draft passed every check.")
    for e in state["rejection_log"]:
        inj = next((h["injected"] for h in state["history"] if h["attempt"] == e["attempt"] and h.get("injected")), None)
        out += [f"## Attempt {e['attempt']}: REJECTED" + (f"  (deliberate fault injected: `{inj}`)" if inj else ""), ""]
        out.append("| Check | What failed | Evidence |")
        out.append("|---|---|---|")
        for f in e["failed"]:
            out.append(f"| {f['check_id']} | {f['reason']} | {f['evidence'].replace('|', '/')[:200]} |")
        if e["skipped_llm_judge"]:
            out.append("\n_LLM judge skipped on this attempt: deterministic checks failed first (saves quota)._")
        out += ["", "**Feedback sent to the generator:**", "", "```", e["feedback_sent"], "```", ""]
        if e.get("changes_made"):
            out += [f"**What changed on retry:** {e['changes_made']}", ""]
        o = e.get("outcome_next_attempt")
        if o:
            out += [f"**Outcome of the retry:** fixed {o['resolved'] or 'none'}; still failing {o['still_failing'] or 'none'}; not yet evaluated {o['not_evaluated_yet'] or 'none'}", ""]
    return "\n".join(out)


def write_attempt(run_dir: Path, n: int, lesson: str):
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"attempt_{n}.md").write_text(lesson, encoding="utf-8")


def write_all(run_dir: Path, state: dict, usage: dict):
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "final_lesson.md").write_text(state["final_lesson"], encoding="utf-8")
    (run_dir / "rejection_log.json").write_text(json.dumps(state["rejection_log"], indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "rejection_log.md").write_text(render_md(state), encoding="utf-8")
    summary = {k: state.get(k) for k in ("topic", "status", "attempt", "best_attempt", "inject", "memory_lessons", "memory_update")}
    summary["usage"] = usage
    summary["attempts"] = [{"attempt": h["attempt"], "injected": h.get("injected"), "verdicts": h["verdicts"]} for h in state["history"]]
    (run_dir / "run.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
