# Rejection log: Introduction to RAG (Retrieval-Augmented Generation)

Final status: **needs_human_review** after 3 attempt(s).

## Attempt 1: REJECTED

| Check | What failed | Evidence |
|---|---|---|
| D2 | Lesson has 672 words; allowed range is 700-1300. | 672 words (allowed 700-1300) |
| D4 | Technical term(s) used without a plain-words explanation: 'context window', 'fine-tuning' | 'context window' first used in: "The LLM’s *context window* limits how much text it can read at one time."; 'fine-tuning' first used in: "RAG is different from fine-tuning." |

_LLM judge skipped on this attempt: deterministic checks failed first (saves quota)._

**Feedback sent to the generator:**

```
- [D2] Lesson has 672 words; allowed range is 700-1300.
  Evidence: 672 words (allowed 700-1300)
  Fix: Add content to reach 700-1300 words.
- [D4] Technical term(s) used without a plain-words explanation: 'context window', 'fine-tuning'
  Evidence: 'context window' first used in: "The LLM’s *context window* limits how much text it can read at one time."; 'fine-tuning' first used in: "RAG is different from fine-tuning."
  Fix: Explain 'context window' in plain words where it first appears (it means the limit on how much text an LLM can read at once). Explain 'fine-tuning' in plain words where it first appears (it means training a model again on new data).
- (Quality checks by the LLM judge run only after the basic checks above pass.)
```

**What changed on retry:** 672→697 words; 7 sentence(s) removed/replaced, 8 added/rewritten; e.g. now: "The LLM’s context window means the limit on how much text the model can read at once." | "Because of this limit, only a few relevant chunks are added instead of all documents."

**Outcome of the retry:** fixed ['D4']; still failing ['D2']; not yet evaluated none

## Attempt 2: REJECTED

| Check | What failed | Evidence |
|---|---|---|
| D2 | Lesson has 697 words; allowed range is 700-1300. | 697 words (allowed 700-1300) |

_LLM judge skipped on this attempt: deterministic checks failed first (saves quota)._

**Feedback sent to the generator:**

```
- [D2] Lesson has 697 words; allowed range is 700-1300.
  Evidence: 697 words (allowed 700-1300)
  Fix: Add content to reach 700-1300 words.
- (Quality checks by the LLM judge run only after the basic checks above pass.)
```

**What changed on retry:** 697→732 words; 0 sentence(s) removed/replaced, 2 added/rewritten; e.g. now: "RAG is useful when a company has many policy PDFs, or a school has many lecture notes." | "Instead of rebuilding a new LLM each year, the same model can read the newest files through RAG."

**Outcome of the retry:** fixed ['D2']; still failing none; not yet evaluated none

## Attempt 3: REJECTED

| Check | What failed | Evidence |
|---|---|---|
| L7 | The lesson does not use an analogy; it provides a concrete example instead. Therefore, the check for an accurate analogy cannot be passed. | MISSING: The lesson does not contain an analogy. |

**Feedback sent to the generator:**

```
- [L7] The lesson does not use an analogy; it provides a concrete example instead. Therefore, the check for an accurate analogy cannot be passed.
  Evidence: MISSING: The lesson does not contain an analogy.
  Fix: Add an analogy that accurately maps to retrieval and generation without suggesting model retraining, or remove the check if analogies are not required.
```
