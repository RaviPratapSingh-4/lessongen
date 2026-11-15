"""Self-evolution: learn from repeated failures. Lessons are auto-applied; rubric changes are human-gated."""
import json

from .llm import LLM, loads_lenient


def reflect(cfg: dict, llm: LLM, store, checks, state: dict, run_id: str, template: str) -> dict:
    by_id = {c.id: c for c in checks}
    reasons: dict[str, list[str]] = {}
    for att in state["history"]:
        if att.get("injected"):  # a deliberately planted fault is not the generator's fault: never learn from it
            continue
        for v in att["verdicts"]:
            if not v["passed"]:
                reasons.setdefault(v["check_id"], []).append(v["reason"])
    store.record_failures({k: len(v) for k, v in reasons.items()}, {k: v[-1] for k, v in reasons.items()})
    counts = store.failure_counts()
    eligible = [k for k in reasons if counts.get(k, 0) >= cfg["lesson_threshold"] and not store.has_lesson(k) and k in by_id]
    update = {"failure_counts_this_run": {k: len(v) for k, v in reasons.items()}, "new_lessons": [], "new_proposals": []}
    if not eligible:
        return update
    failures = [{"check_id": k, "description": by_id[k].description, "reason": reasons[k][-1], "fix_hint": by_id[k].fix_hint} for k in eligible]
    existing = [l["text"] for l in store.active_lessons(20)]
    user = template.replace("<<FAILURES>>", json.dumps(failures, indent=1)).replace("<<EXISTING>>", "\n".join(existing) or "(none)")
    try:
        data = loads_lenient(llm.chat("reflector", "You return only JSON.", user, json_mode=True, meta={"failures": failures}).text)
    except Exception:  # reflection is best-effort and must never break a run
        data = {"lessons": [{"check_id": f["check_id"], "text": f["fix_hint"]} for f in failures], "rubric_proposals": []}
    for l in data.get("lessons", [])[: len(eligible)]:
        if l.get("check_id") in eligible and l.get("text"):
            store.add_lesson(l["check_id"], l["text"].strip(), run_id)
            update["new_lessons"].append({"check_id": l["check_id"], "text": l["text"].strip()})
    for p in data.get("rubric_proposals", [])[:1]:
        if p.get("description") and (pid := store.add_proposal(p["description"].strip(), p.get("fix_hint", "").strip(), run_id)):
            update["new_proposals"].append({"id": pid, "description": p["description"].strip()})
    return update
