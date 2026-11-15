# Rejection log: Introduction to RAG (Retrieval-Augmented Generation)

Final status: **passed** after 2 attempt(s).

## Attempt 1: REJECTED  (deliberate fault injected: `false_claim`)

| Check | What failed | Evidence |
|---|---|---|
| D2 | Lesson has 692 words; allowed range is 700-1300. | 692 words (allowed 700-1300) |
| D4 | Technical term(s) used without a plain-words explanation: 'prompt' | 'prompt' first used in: "The retrieved chunks are placed in the prompt together with the question (this is called augmentation)." |
| L1 | The lesson states that RAG retrains the model's weights, which contradicts F12 and F14 from the fact sheet. | RAG works by retraining the model's weights every time a user asks a question. |
| L2 | The statement that RAG retrains the model's weights is a factual error, as RAG only changes the input to the model, not the model itself. | RAG works by retraining the model's weights every time a user asks a question. |
| L6 | The lesson introduces a fundamentally incorrect concept about RAG (retraining the model) at the beginning of the 'How does it work?' section, which contradicts the core mechanism explained immediately after and disrupts the logical flow. | RAG works by retraining the model's weights every time a user asks a question. |

**Feedback sent to the generator:**

```
- [D2] Lesson has 692 words; allowed range is 700-1300.
  Evidence: 692 words (allowed 700-1300)
  Fix: Add about 158 words (8 below the minimum): more detail in 'How does it work?' and the example.
- [D4] Technical term(s) used without a plain-words explanation: 'prompt'
  Evidence: 'prompt' first used in: "The retrieved chunks are placed in the prompt together with the question (this is called augmentation)."
  Fix: Explain 'prompt' in plain words where it first appears (it means the text given to an LLM).
- [L1] The lesson states that RAG retrains the model's weights, which contradicts F12 and F14 from the fact sheet.
  Evidence: RAG works by retraining the model's weights every time a user asks a question.
  Fix: Remove the sentence 'RAG works by retraining the model's weights every time a user asks a question.' as it is factually incorrect and contradicts the provided fact sheet.
- [L2] The statement that RAG retrains the model's weights is a factual error, as RAG only changes the input to the model, not the model itself.
  Evidence: RAG works by retraining the model's weights every time a user asks a question.
  Fix: Remove the sentence 'RAG works by retraining the model's weights every time a user asks a question.' as it is a factual error.
- [L6] The lesson introduces a fundamentally incorrect concept about RAG (retraining the model) at the beginning of the 'How does it work?' section, which contradicts the core mechanism explained immediately after and disrupts the logical flow.
  Evidence: RAG works by retraining the model's weights every time a user asks a question.
  Fix: Remove the sentence 'RAG works by retraining the model's weights every time a user asks a question.' to ensure a logical flow where concepts are explained correctly and without contradiction.
```

**What changed on retry:** 692→825 words; 27 sentence(s) removed/replaced, 37 added/rewritten; e.g. now: "Retrieval-Augmented Generation (RAG) is a method that gives a large language model extra information before it" | "RAG solves the problem by first retrieving relevant information from an external knowledge source and then giv"

**Outcome of the retry:** fixed ['D2', 'D4', 'L1', 'L2', 'L6']; still failing none; not yet evaluated none
