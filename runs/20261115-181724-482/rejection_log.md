# Rejection log: Introduction to RAG (Retrieval-Augmented Generation)

Final status: **needs_human_review** after 3 attempt(s).

## Attempt 1: REJECTED  (deliberate fault injected: `false_claim`)

| Check | What failed | Evidence |
|---|---|---|
| D4 | Technical term(s) used without a plain-words explanation: 'vector database', 'prompt' | 'vector database' first used in: "All embeddings are stored in a vector database."; 'prompt' first used in: "The retrieved chunks are added to the prompt together with the question." |

_LLM judge skipped on this attempt: deterministic checks failed first (saves quota)._

**Feedback sent to the generator:**

```
- [D4] Technical term(s) used without a plain-words explanation: 'vector database', 'prompt'
  Evidence: 'vector database' first used in: "All embeddings are stored in a vector database."; 'prompt' first used in: "The retrieved chunks are added to the prompt together with the question."
  Fix: Explain 'vector database' in plain words where it first appears (it means a storage that quickly finds items with similar meaning). Explain 'prompt' in plain words where it first appears (it means the text given to an LLM).
- (Quality checks by the LLM judge run only after the basic checks above pass.)
```

**What changed on retry:** 747→708 words; 18 sentence(s) removed/replaced, 12 added/rewritten; e.g. now: "It is a method that helps a large language model ( LLM ) give better answers." | "An LLM is a computer program that writes text by predicting the most likely next word."

**Outcome of the retry:** fixed ['D4']; still failing none; not yet evaluated none

## Attempt 2: REJECTED

| Check | What failed | Evidence |
|---|---|---|
| L5 | The word 'incur' is a slightly more formal and less common word than simpler alternatives like 'get' or 'face', which could be challenging for a non-native English reader. | Late submissions incur a penalty. |
| L8 | Unverified pass: the judge's evidence quote was not found in the lesson. | Answer: “The deadline to submit the final project for the Data Science course is 15 September.” ... Chunk 1: “Data Science – Project Guidelines. The final project must be submitted by 15 September.” . |

**Feedback sent to the generator:**

```
- [L5] The word 'incur' is a slightly more formal and less common word than simpler alternatives like 'get' or 'face', which could be challenging for a non-native English reader.
  Evidence: Late submissions incur a penalty.
  Fix: Replace 'incur a penalty' with a simpler phrase like 'will get a penalty' or 'face a penalty'.
- [L8] Unverified pass: the judge's evidence quote was not found in the lesson.
  Evidence: Answer: “The deadline to submit the final project for the Data Science course is 15 September.” ... Chunk 1: “Data Science – Project Guidelines. The final project must be submitted by 15 September.” ... Chunk 2: “Course Calendar. ... Final project deadline on 15 September.”
  Fix: Rewrite the example answer using only the words and facts in the retrieved chunks.
```

**What changed on retry:** 708→709 words; 3 sentence(s) removed/replaced, 3 added/rewritten; e.g. now: "It is a method that helps a large language model (LLM) give better answers." | "All embeddings are stored in a vector database, a storage system that can quickly find items whose numbers are"

**Outcome of the retry:** fixed ['L5']; still failing ['L8']; not yet evaluated none

## Attempt 3: REJECTED

| Check | What failed | Evidence |
|---|---|---|
| L8 | Unverified pass: the judge's evidence quote was not found in the lesson. | Answer: “The deadline to submit the final project for the Data Science course is 15 September.” ... Chunk 1: “Data Science – Project Guidelines. The final project must be submitted by 15 September.” |

**Feedback sent to the generator:**

```
- [L8] Unverified pass: the judge's evidence quote was not found in the lesson.
  Evidence: Answer: “The deadline to submit the final project for the Data Science course is 15 September.” ... Chunk 1: “Data Science – Project Guidelines. The final project must be submitted by 15 September.”
  Fix: Rewrite the example answer using only the words and facts in the retrieved chunks.
```
