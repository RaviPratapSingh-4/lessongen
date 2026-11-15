# Rejection log: Introduction to RAG (Retrieval-Augmented Generation)

Final status: **passed** after 2 attempt(s).

## Attempt 1: REJECTED

| Check | What failed | Evidence |
|---|---|---|
| D4 | Technical term(s) used without a plain-words explanation: 'prompt' | 'prompt' first used in: "The retrieved text is augmented to the LLM’s prompt, so the model can use up‑to‑date or private information w…" |

_LLM judge skipped on this attempt: deterministic checks failed first (saves quota)._

**Feedback sent to the generator:**

```
- [D4] Technical term(s) used without a plain-words explanation: 'prompt'
  Evidence: 'prompt' first used in: "The retrieved text is augmented to the LLM’s prompt, so the model can use up‑to‑date or private information w…"
  Fix: Explain 'prompt' in plain words where it first appears (it means the text given to an LLM).
- (Quality checks by the LLM judge run only after the basic checks above pass.)
```

**What changed on retry:** 834→848 words; 3 sentence(s) removed/replaced, 4 added/rewritten; e.g. now: "It helps a large language model (LLM) answer questions more accurately." | "The retrieved text is augmented to the LLM’s prompt (the prompt is the text given to the LLM)."

**Outcome of the retry:** fixed ['D4']; still failing none; not yet evaluated none
