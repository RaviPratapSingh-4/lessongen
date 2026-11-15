import re

from .llm import LLM


def format_feedback(verdicts: list[dict], skipped_judge: bool = False) -> str:
    lines = []
    for v in verdicts:
        if not v["passed"]:
            lines.append(f"- [{v['check_id']}] {v['reason']}\n  Evidence: {v['evidence']}\n  Fix: {v['fix']}")
    if skipped_judge:
        lines.append("- (Quality checks by the LLM judge run only after the basic checks above pass.)")
    return "\n".join(lines)


def build_prompt(template: str, topic: str, facts: str, lessons: list[str], prev: str | None = None, feedback: str | None = None) -> str:
    memory = ""
    if lessons:
        memory = "\nLESSONS LEARNED FROM PAST RUNS (follow them):\n" + "\n".join(f"- {t}" for t in lessons) + "\n"
    revision = ""
    if prev and feedback:
        revision = (
            "\nREVISION FEEDBACK: your previous draft was rejected by the reviewer. Fix ONLY the problems below. "
            "Keep everything that already works. Output the complete corrected lesson.\n"
            f"PROBLEMS:\n{feedback}\n\nPREVIOUS DRAFT:\n{prev}\n"
        )
    return template.replace("<<TOPIC>>", topic).replace("<<FACTS>>", facts).replace("<<MEMORY>>", memory).replace("<<REVISION>>", revision)


def clean(text: str) -> str:
    t = text.strip()
    t = re.sub(r"^```(?:markdown|md)?\s*\n|\n```$", "", t)
    t = t.replace("\u2010", "-").replace("\u2011", "-").replace("\u00a0", " ")
    return t.strip() + "\n"


def generate(llm: LLM, template: str, topic: str, facts: str, lessons: list[str], attempt: int, inject: bool, prev=None, feedback=None) -> str:
    user = build_prompt(template, topic, facts, lessons, prev, feedback)
    resp = llm.chat("generator", "You are an expert teacher writing for beginners.", user, meta={"attempt": attempt, "inject": inject})
    return clean(resp.text)
