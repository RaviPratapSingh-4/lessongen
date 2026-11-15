"""Deliberate fault injection: plant a known defect in a draft to prove the evaluator catches it."""
import re

FALSE_CLAIM = "RAG works by retraining the model's weights every time a user asks a question."
JARGON = "Under the hood, RAG relies on vector embeddings, chunking and semantic retrieval over a knowledge base."
LONG_SENTENCE = (
    "In addition to everything that we have discussed so far in this lesson, it is also worth remembering that the whole "
    "process, from the moment a person types a question to the moment the answer appears on the screen, happens in a few "
    "seconds without the person ever noticing it."
)


def _insert_after(text: str, heading_kw: str, sentence: str, paragraphs: int = 1) -> str:
    lines = text.split("\n")
    h = next((i for i, l in enumerate(lines) if l.lstrip().startswith("#") and heading_kw in l.lower()), None)
    if h is None:
        return text + "\n\n" + sentence
    i, seen = h + 1, 0
    while i < len(lines):
        if lines[i].strip() and not lines[i].lstrip().startswith("#"):
            seen += 1
            if seen == paragraphs:
                lines.insert(i + 1, "\n" + sentence)
                return "\n".join(lines)
        i += 1
    return text + "\n\n" + sentence


def false_claim(text: str) -> str:
    return _insert_after(text, "how does", FALSE_CLAIM)


def jargon(text: str) -> str:
    lines = text.split("\n")
    h = next(i for i, l in enumerate(lines) if l.startswith("## "))
    lines[h + 1 : h + 1] = ["", JARGON]
    return "\n".join(lines)


def long_sentence(text: str) -> str:
    return _insert_after(text, "what is", LONG_SENTENCE)


def no_recap(text: str) -> str:
    return re.split(r"\n## Recap", text)[0].rstrip() + "\n"


def too_short(text: str) -> str:
    lines = text.split("\n")
    return "\n".join(lines[: int(len(lines) * 0.35)])


# name -> (function, check ids that MUST fail)
VARIANTS = {
    "false_claim": (false_claim, ["L1", "L2"]),  # judged by the LLM (L1/L2)
    "jargon": (jargon, ["D4"]),
    "long_sentence": (long_sentence, ["D3"]),
    "no_recap": (no_recap, ["D1", "D6"]),
    "too_short": (too_short, ["D2"]),
}


def apply(name: str, text: str) -> str:
    return VARIANTS[name][0](text)
