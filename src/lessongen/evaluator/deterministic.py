"""Code-based rubric checks: free, repeatable, objective. Each returns a Verdict with code-generated evidence."""
import re

import yaml

from ..config import ROOT
from ..schemas import Check, Verdict

_HEAD = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
_BULLET = re.compile(r"^\s*([-*•]|\d+[.)])\s+")
_WORD = re.compile(r"[A-Za-z0-9'’\-]+")


def sections(text: str) -> list[tuple[str, str]]:
    out, head, buf = [], "", []
    for line in text.split("\n"):
        m = _HEAD.match(line)
        if m:
            out.append((head, "\n".join(buf)))
            head, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    out.append((head, "\n".join(buf)))
    return [(h, b) for h, b in out if h or b.strip()]


def strip_md(text: str) -> str:
    """Prose only: no code blocks, no headings, no list markers, no emphasis marks."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    lines = []
    for l in text.split("\n"):
        if _HEAD.match(l):
            continue
        l = _BULLET.sub("", l).replace("**", "").replace("__", "").replace("`", "").lstrip("> ")
        lines.append(l)
    return "\n".join(lines)


def words(s: str) -> list[str]:
    return _WORD.findall(s)


def sentences(prose: str) -> list[str]:
    parts = []
    for line in prose.split("\n"):
        parts += re.split(r"(?<=[.!?])\s+", line.strip())
    return [p for p in parts if words(p)]


def _short(s: str, n: int = 150) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def _v(cid, passed, evidence, reason="", fix=""):
    return Verdict(check_id=cid, passed=passed, evidence=evidence, reason=reason, fix=fix, source="det")


def d1(text, cfg, chk):
    heads = " | ".join(h.lower() for h, _ in sections(text) if h)
    need = {"What": ["what"], "Why": ["why"], "How": ["how"], "Example": ["example"], "Recap": ["recap", "summary", "takeaway"]}
    missing = [k for k, kws in need.items() if not any(kw in heads for kw in kws)]
    return _v("D1", not missing, f"headings found: {heads or 'none'}", f"Missing section(s): {', '.join(missing)}" if missing else "", chk.fix_hint if missing else "")


def d2(text, cfg, chk):
    n, lo, hi = len(words(strip_md(text))), cfg["limits"]["min_words"], cfg["limits"]["max_words"]
    ok = lo <= n <= hi
    if ok:
        fix = ""
    elif n < lo:
        fix = f"Add about {lo - n + 150} words ({lo - n} below the minimum): more detail in 'How does it work?' and the example."
    else:
        fix = f"Remove about {n - hi + 100} words."
    return _v("D2", ok, f"{n} words (allowed {lo}-{hi})", "" if ok else f"Lesson has {n} words; allowed range is {lo}-{hi}.", fix)

def d3(text, cfg, chk):
    sents = sentences(strip_md(text))
    lens = [len(words(s)) for s in sents]
    avg, mx = sum(lens) / max(len(lens), 1), max(lens, default=0)
    la, lm = cfg["limits"]["max_avg_sentence_words"], cfg["limits"]["max_sentence_words"]
    longest = sents[lens.index(mx)] if lens else ""
    ok = avg <= la and mx <= lm
    why = []
    if avg > la:
        why.append(f"average sentence is {avg:.1f} words (max {la})")
    if mx > lm:
        why.append(f"a sentence has {mx} words (max {lm}): \"{_short(longest)}\"")
    return _v("D3", ok, f"avg {avg:.1f} words, longest {mx} words", "; ".join(why), "" if ok else chk.fix_hint + (f" Rewrite this sentence as 2-3 short ones: \"{_short(longest)}\"" if mx > lm else ""))


def _defined(term: str, window: str) -> bool:
    T = re.escape(term) + "s?"
    pats = [
        rf"\b{T}\b[^.!?]{{0,30}}?\b(means|is|are|stands for|refers to)\b",
        rf"\b(called|known as|named)\s+(?:a |an |the )?{T}\b",
        rf"\bcall(?:s|ed)?\b[^.!?]{{0,25}}\b{T}\b",
        rf"\b{T}\b\s*\(",
        rf"\({T}\)",
        rf"\b{T}\b\s+[—–-]\s+",
        rf"\b{T}\b,\s+(which|a|an|the)\b",
    ]
    return any(re.search(p, window, re.I) for p in pats)


def d4(text, cfg, chk):
    terms = yaml.safe_load((ROOT / "data" / "jargon.yaml").read_text(encoding="utf-8"))["terms"]
    sents = sentences(strip_md(text))
    bad = []
    for t in terms:
        rx = re.compile(rf"\b{re.escape(t['term'])}s?\b", re.I)
        i = next((k for k, s in enumerate(sents) if rx.search(s)), None)
        if i is not None and not _defined(t["term"], " ".join(sents[i : i + 2])):
            bad.append((t, sents[i]))
    if not bad:
        return _v("D4", True, "all watchlist terms explained at first use")
    names = ", ".join(f"'{t['term']}'" for t, _ in bad)
    ev = "; ".join(f"'{t['term']}' first used in: \"{_short(s, 110)}\"" for t, s in bad[:3])
    fix = " ".join(f"Explain '{t['term']}' in plain words where it first appears (it means {t['plain']})." for t, _ in bad)
    return _v("D4", False, ev, f"Technical term(s) used without a plain-words explanation: {names}", fix)


def d5(text, cfg, chk):
    n = max((len(words(strip_md(b))) for h, b in sections(text) if "example" in h.lower()), default=0)
    need = cfg["limits"]["min_example_words"]
    return _v("D5", n >= need, f"example section has {n} words (min {need})", "" if n >= need else "No worked example section with enough content.", "" if n >= need else chk.fix_hint)


def d6(text, cfg, chk):
    body = next((b for h, b in sections(text) if any(k in h.lower() for k in ("recap", "summary", "takeaway"))), "")
    n, need = sum(1 for l in body.split("\n") if _BULLET.match(l)), cfg["limits"]["min_recap_bullets"]
    return _v("D6", n >= need, f"recap has {n} bullet points (min {need})", "" if n >= need else f"Recap has {n} bullet point(s); need at least {need}.", "" if n >= need else chk.fix_hint)


DET = {"D1": d1, "D2": d2, "D3": d3, "D4": d4, "D5": d5, "D6": d6}


def run_deterministic(text: str, checks: list[Check], cfg: dict) -> list[Verdict]:
    return [DET[c.id](text, cfg, c) for c in checks if c.type == "det"]
