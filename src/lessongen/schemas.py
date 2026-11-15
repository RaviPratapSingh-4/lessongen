from typing import Literal

from pydantic import BaseModel


class Check(BaseModel):
    id: str
    type: Literal["det", "llm"]
    description: str
    fix_hint: str = ""


class Verdict(BaseModel):
    """One binary verdict. `evidence` is code-generated for det checks and a verified quote for llm checks."""

    check_id: str
    passed: bool
    evidence: str = ""
    reason: str = ""
    fix: str = ""
    source: Literal["det", "llm"] = "det"
