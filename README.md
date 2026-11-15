# Self-Evaluating Lesson Generator

An agentic **generate → evaluate → regenerate** system. It writes a beginner lesson ("Introduction to RAG") for a 12th-grade learner from India with limited English, judges the lesson against a hard pass/fail rubric, and regenerates with the failure reasons until it passes. If it cannot pass within the retry limit, it ships the best attempt flagged `needs_human_review` and never hides the failure.

Output of every run: the lesson, a rejection log (what failed, why, what changed on retry), and the full run record.

## Quick start

Requires Python 3.10+ and two free API keys (Groq, Google Gemini).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
copy .env.example .env      # then put GROQ_API_KEY and GEMINI_API_KEY in .env
pytest -q                   # 11 tests, no API calls
```

| Command                                                          | What it does                                                                                                                                             |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lessongen --mock run`                                         | Full loop on an offline mock LLM (0 tokens)                                                                                                              |
| `lessongen run`                                                | Real run: generate → evaluate → regenerate                                                                                                             |
| `lessongen run --inject false_claim`                           | Plants a deliberate false claim in attempt 1 to prove the evaluator catches it. Other faults: `jargon`, `long_sentence`, `no_recap`, `too_short` |
| `lessongen eval-fixtures --llm`                                | Evaluator self-test on a good lesson and broken variants                                                                                                 |
| `lessongen memory`                                             | Learned lessons, failure counts, rubric proposals, recent runs                                                                                           |
| `lessongen rubric review` / `approve <id>` / `reject <id>` | Human approval of rubric changes proposed by the system                                                                                                  |

All settings (models, retries, word limits, memory threshold) are in `config.yaml`.

## Architecture

```
generate → deterministic checks ─fail→ log_rejection ─→ generate (retry, max 2)
                  │pass
                  ▼
             LLM judge ─fail→ log_rejection ─→ generate (retry)
                  │pass
                  ▼
   finalize → reflect (update memory) → END
```

Built with LangGraph and Python. After 3 attempts (1 + 2 retries) the loop always stops; the best attempt is returned as `needs_human_review`.

| Role      | Model                        | Why                                                                                                      |
| --------- | ---------------------------- | -------------------------------------------------------------------------------------------------------- |
| Generator | Groq `openai/gpt-oss-120b` | Fast, free tier                                                                                          |
| Judge     | Gemini `gemini-2.5-flash`  | Different provider and model family from the generator, so it does not share the generator's blind spots |
| Reflector | Groq `openai/gpt-oss-20b`  | Small task, cheap                                                                                        |

### Hybrid evaluator (14 hard pass/fail checks, no partial credit)

Six checks are plain code: free, repeatable, run first. The LLM judge runs only if they pass, which saves quota.

| ID | Check                                                                               |
| -- | ----------------------------------------------------------------------------------- |
| D1 | Required sections present (What / Why / How / Example / Recap)                      |
| D2 | Length 700-1300 words                                                               |
| D3 | Short sentences (average ≤ 17 words, longest ≤ 32)                                |
| D4 | Watchlist technical terms explained in plain words at first use                     |
| D5 | Worked-example section with enough content                                          |
| D6 | Recap has enough bullet points                                                      |
| L1 | Grounded: every technical claim is in the fact sheet (`data/facts.md`)            |
| L2 | Accurate: no factual errors or misleading statements                                |
| L3 | Coverage: every `[MUST]` fact is explained                                        |
| L4 | Example is concrete and set in an Indian student context                            |
| L5 | Language is simple for a non-native English reader                                  |
| L6 | Ideas appear in a logical order                                                     |
| L7 | Analogy is accurate (never suggests the model is retrained)                         |
| L8 | Example grounding: the example's answer uses only the facts in its retrieved chunks |

The lesson ships only if **all** checks pass. L8 was added after a manual review found a real flaw the judge had missed: an example answer contained a detail not present in its retrieved chunk. That gap-then-new-check cycle is the rubric improving itself.

### Judge reliability controls

- Temperature 0, JSON-only output, one retry on bad JSON.
- Each verdict has `check_id, passed, evidence, reason, fix`.
- A PASS must include a quote that is actually found in the lesson (fuzzy match ≥ 80% word coverage). Otherwise it is flipped to a fail.
- Missing or malformed verdicts fail closed.

### Memory and self-evolution

- SQLite (`memory.db`) behind a `MemoryStore` interface. Tables: runs, check failures, lessons, rubric proposals.
- When a check fails `lesson_threshold` times (default 2, counted across attempts and runs), the reflector writes a short **lesson**. Lessons are injected into the next generator prompt.
- **Rubric changes are human-gated.** The reflector can only *propose*; a person approves with `lessongen rubric approve <id>`. Deliberately injected faults are never learned from.

### Token strategy

Prompt-hash disk cache (identical calls cost 0 tokens), `--mock` mode, deterministic checks before the LLM judge, one judge call per attempt.

## Results (from real runs; see `runs/`)

| Run                     | Result                                                                                                                                                                                             |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `20261115-165415-285` | Attempt 1 rejected on D4 (term used before it was explained); attempt 2 passed all 13 checks (rubric v1)                                                                                           |
| `20261115-172024-667` | `needs_human_review` after 3 attempts (D2 length, D2, then L7: no analogy). The generator undershot the word limit and dropped the analogy; both were fixed in the prompt afterwards             |
| `20261115-173404-411` | Attempt 1 rejected on D4; attempt 2 passed all 14 checks                                                                                                                                           |
| `20261115-181724-482` | Deliberate false claim: attempt 1 was rejected on D4 before the judge ran, so the false claim was not judged; `needs_human_review` (see Limitations 2 and 3)                                     |
| `20261115-182322-816` | Deliberate false claim, after the fix that always judges injected attempts: attempt 1 rejected on **L1, L2, L6** (plus D2, D4); attempt 2 passed. **Final lesson comes from this run** |

`lessongen eval-fixtures --llm`: the good lesson passes; the `false_claim` variant fails L1 and L2 (the judge also flagged other checks); `jargon` fails D4, `long_sentence` D3, `no_recap` D1+D6, `too_short` D1+D2+D5+D6.

Rejection logs are in `runs/<run_id>/rejection_log.md` and `.json`.

## Limitations (implemented behaviour, not hidden)

1. **D4 is a regex heuristic** over a watchlist (`data/jargon.yaml`). It checks a term is explained in the sentence of first use or the next, not that the explanation is good.
2. **The judge sometimes breaks its own evidence rule.** Gemini occasionally answered "pass" with `MISSING:` evidence, or with a quote stitched from several places using "...". The verifier then flips the pass to a fail. This is safe (fail-closed) but can cause a false rejection; it happened for L8 in run `20261115-181724-482`.
3. **Fail-fast order hides LLM checks.** When a deterministic check fails, the judge is skipped to save quota, so a lesson's LLM-judged problems appear only after the basic checks pass. For injected faults the judge always runs.
4. **Reflector lessons are generic.** For example, the learned D2 lesson restates the length rule. The reflector does not see measured word counts.
5. **One topic, small sample.** Results come from a handful of runs, not a benchmark. The rubric-proposal approval flow exists and is unit-tested but was not exercised in a real run.

## Proposed, not implemented

- pgvector or semantic memory for many topics (not needed for one topic and a tiny memory).
- Passing measured numbers (word counts, sentence lengths) to the reflector.
- A richer D4 using the model to check explanation quality.
- A Streamlit viewer over `runs/` and `memory.db`.

## Project layout

```
config.yaml   data/{facts.md,jargon.yaml,rubric.yaml}   prompts/{generator,judge,reflector}.md
src/lessongen/{cli,config,schemas,llm,generator,graph,reflector,logbook,inject,mock_backend}.py
src/lessongen/evaluator/{deterministic,judge,rubric}.py   src/lessongen/memory/{base,sqlite_store}.py
tests/   runs/<run_id>/{attempt_N.md, final_lesson.md, rejection_log.md/json, run.json}
```
