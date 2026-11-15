You improve a lesson-writing system by learning from its failures.

These rubric checks failed repeatedly (check id, description, recent failure reasons, fix hint):
<<FAILURES>>

Lessons already stored (do not repeat them):
<<EXISTING>>

Return ONLY this JSON:
{"lessons":[{"check_id":"D4","text":"..."}],"rubric_proposals":[{"description":"...","fix_hint":"..."}]}

Rules:
- Write at most one lesson per failed check id. Each "text" is ONE imperative instruction (max 30 words) that a lesson writer can follow, specific to the failure pattern.
- Propose at most ONE new rubric check, and only if the failures reveal a quality problem no existing check covers. Otherwise return an empty list.
