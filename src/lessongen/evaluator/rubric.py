import yaml

from ..config import ROOT
from ..schemas import Check


def load_rubric(store=None) -> list[Check]:
    data = yaml.safe_load((ROOT / "data" / "rubric.yaml").read_text(encoding="utf-8"))
    checks = [Check(**c) for c in data["checks"]]
    if store:  # human-approved checks learned by the reflector (self-evolving rubric)
        for p in store.approved_checks():
            checks.append(Check(id=p["check_id"], type="llm", description=p["description"], fix_hint=p["fix_hint"]))
    return checks
