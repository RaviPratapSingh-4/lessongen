"""Offline stand-in for the LLM so the loop, parsing and memory can be tested with zero API calls."""
import json
import re

from . import inject
from .config import ROOT

GOOD = ROOT / "tests" / "fixtures" / "good.md"


def _quote(lesson: str) -> str:
    line = next(l for l in lesson.split("\n") if l.strip() and not l.lstrip().startswith("#"))
    return line.strip()[:80]


def respond(role: str, system: str, user: str, meta: dict) -> str:
    good = GOOD.read_text(encoding="utf-8")
    if role == "generator":
        if "REVISION FEEDBACK" in user or meta.get("inject"):
            return good  # retry draft, or a clean draft that the pipeline will then sabotage on purpose
        return inject.long_sentence(inject.jargon(good))  # a naturally flawed first draft
    if role == "judge":
        lesson = meta["lesson"]
        bad = next((s for s in re.split(r"(?<=[.!?])\s+", lesson) if "retrain" in s.lower() and "weights" in s.lower() and "does not" not in s.lower()), None)
        out = []
        for cid in meta["check_ids"]:
            if bad and cid in ("L1", "L2"):
                out.append({"check_id": cid, "passed": False, "evidence": bad.strip(), "reason": "States that RAG retrains the model, which contradicts the fact sheet (F5, F12).", "fix": "Remove this claim. RAG does not change the model; it only changes the input."})
            else:
                out.append({"check_id": cid, "passed": True, "evidence": _quote(lesson), "reason": "Mock judge: ok.", "fix": ""})
        return json.dumps({"verdicts": out})
    if role == "reflector":
        fails = meta.get("failures", [])
        lessons = [{"check_id": f["check_id"], "text": f["fix_hint"] or f["reason"]} for f in fails]
        props = []
        if any(f["check_id"] == "L2" for f in fails):
            props = [{"description": "The lesson never claims that RAG retrains or changes the model's weights.", "fix_hint": "Remove any claim that RAG retrains the model."}]
        return json.dumps({"lessons": lessons, "rubric_proposals": props})
    raise ValueError(role)
