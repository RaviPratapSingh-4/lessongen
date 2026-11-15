# Rejection log: Introduction to RAG (Retrieval-Augmented Generation)

Final status: **passed** after 2 attempt(s).

## Attempt 1: REJECTED

| Check | What failed | Evidence |
|---|---|---|
| D4 | Technical term(s) used without a plain-words explanation: 'fine-tuning' | 'fine-tuning' first used in: "Updating a knowledge base is easier than fine-tuning the whole model." |

_LLM judge skipped on this attempt: deterministic checks failed first (saves quota)._

**Feedback sent to the generator:**

```
- [D4] Technical term(s) used without a plain-words explanation: 'fine-tuning'
  Evidence: 'fine-tuning' first used in: "Updating a knowledge base is easier than fine-tuning the whole model."
  Fix: Explain 'fine-tuning' in plain words where it first appears (it means training a model again on new data).
- (Quality checks by the LLM judge run only after the basic checks above pass.)
```

**What changed on retry:** 718→708 words; 3 sentence(s) removed/replaced, 3 added/rewritten; e.g. now: "Updating a knowledge base is easier than fine-tuning." | "Fine-tuning means training the model again on new data to change its internal knowledge."

**Outcome of the retry:** fixed ['D4']; still failing none; not yet evaluated none
