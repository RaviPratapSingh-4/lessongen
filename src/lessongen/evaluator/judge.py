"""LLM judge: one call for all LLM-judged checks. Built to be hard to fool and to fail closed."""
import json
import re
from difflib import SequenceMatcher

from ..llm import LLM, loads_lenient
from ..schemas import Check, Verdict


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*_`#>]", "", s)).strip().lower()


def _quote_in_lesson(quote: str, lesson: str, threshold: float = 0.8) -> bool:
    q, l = _norm(quote).rstrip(".… "), _norm(lesson)
    if len(q) < 8:
        return False
    if q in l:
        return True
    qw, lw = re.findall(r"\w+", q), re.findall(r"\w+", l)
    if len(qw) < 4:
        return False
    m = SequenceMatcher(None, qw, lw, autojunk=False)
    return sum(b.size for b in m.get_matching_blocks()) / len(qw) >= threshold


def run_judge(llm: LLM, checks: list[Check], lesson: str, facts: str, template: str) -> list[Verdict]:
    llm_checks = [c for c in checks if c.type == "llm"]
    ids = [c.id for c in llm_checks]
    user = (
        template.replace("<<FACTS>>", facts)
        .replace("<<CHECKS>>", "\n".join(f"{c.id}: {c.description}" for c in llm_checks))
        .replace("<<LESSON>>", lesson)
        .replace("<<IDS>>", ", ".join(ids))
    )
    data = None
    for _ in range(2):  # one retry on malformed output (bad replies are never cached)
        resp = llm.chat("judge", "You are a strict JSON-only reviewer.", user, json_mode=True, meta={"check_ids": ids, "lesson": lesson})
        try:
            data = loads_lenient(resp.text)
            break
        except json.JSONDecodeError:
            continue
    items = {}
    if isinstance(data, dict):
        items = {str(v.get("check_id")): v for v in data.get("verdicts", []) if isinstance(v, dict)}
    out = []
    for c in llm_checks:
        v = items.get(c.id)
        if v is None:  # fail closed: no verdict means no pass
            out.append(Verdict(check_id=c.id, passed=False, evidence="", reason="Judge returned no usable verdict (fail-closed).", fix=c.fix_hint, source="llm"))
            continue
        passed = v.get("passed") is True or str(v.get("passed")).lower() == "true"
        evidence, reason, fix = str(v.get("evidence", "")), str(v.get("reason", "")), str(v.get("fix", "")) or c.fix_hint
        if passed and not _quote_in_lesson(evidence, lesson):  # anti-rubber-stamp: a pass must be proven by a real quote
            passed, reason = False, "Unverified pass: the judge's evidence quote was not found in the lesson."
        out.append(Verdict(check_id=c.id, passed=passed, evidence=evidence, reason=reason, fix="" if passed else fix, source="llm"))
    return out
