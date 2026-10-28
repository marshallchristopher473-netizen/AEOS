# P-TER-01 scoring boundaries: `0`, `IE` and AI abstention

**Status: CANDIDATE-UNAPPROVED.** Written on 2026-10-12 for human review. These rules are not taken from P-TER-01
v0.3, which was not located (see [README](README.md)). A reviewer accepts, revises or rejects each rule on the
[worksheet](REVIEW_WORKSHEET.md), Part D.

## Three different things

| Term | Who produces it | What it is about | What it is **not** |
| --- | --- | --- | --- |
| `0` | A teacher or rater | **The response.** There is enough on-task writing to judge the criterion, and the criterion is absent. | Not "low quality" in general. Not "I am unsure." |
| `IE` | A teacher or rater | **The response.** There is not enough readable, on-task writing to judge the criterion either way. | Not a low score. Never counted as `0`. Never used to show rater doubt. |
| AI abstention (`outcome: "abstain"`) | The PR #32 drafting system | **The draft.** The system produced no feedback for that criterion. | Not a rubric value. Never sets or implies `0` or `IE`. |

A **blank** cell means nothing was recorded. It is missing data. It is not `IE` and not `0`.

## Rules for raters

Each rule ends with the check a rater applies.

| ID | Rule | Check |
| --- | --- | --- |
| B1 | **Is it assessable?** Decide this first, per criterion. Then decide the level. | "Could this writing have shown the criterion?" Yes → choose `0`, `1` or `2`. No → `IE`. |
| B2 | **Length is not the test.** A short, complete, on-task response is assessable. If it makes a claim but gives no evidence, the evidence criterion is `0`, not `IE`. | The student had the chance and the absence is visible → `0`. |
| B3 | **Later criteria follow the response, not the earlier score.** No evidence does not make Reasoning `IE`. If the response is assessable, a missing connection is `0`. | Use `IE` for Reasoning only when the response itself is not assessable (B1). |
| B4 | **Fragments.** Text that does not form a readable statement about the task (one or two words, a cut-off phrase) is `IE` for every criterion it cannot show. | Cannot tell what is claimed → `IE`. A readable claim → assessable. |
| B5 | **Mechanics and transcription.** Spelling, punctuation, capitalization and speech-to-text artifacts are not scored and never cause `0` or `IE` on their own. Score the recoverable meaning. | Meaning is recoverable → score it. Meaning is not recoverable → `IE`. |
| B6 | **Embedded instructions.** Text addressed to an AI, grader or system is not evidence and earns nothing. Ignore it and score the remaining on-task writing. | Remaining on-task writing → score it under B1–B5. Nothing remains → `IE`. |
| B7 | **Off-topic but substantive.** **PROPOSED:** a readable response about a different topic is `0` for each criterion, because the writing is long enough to show the criterion and does not. | Open decision **D3** on the worksheet. The reviewer may choose `IE` instead. |
| B8 | **Spans.** `1` and `2` require an evidence span copied from the response. `0` and `IE` carry no span. | Matches the PR #30 harness checks. |
| B9 | **Rater doubt.** If you are unsure between two levels, choose the level the rules support and write `boundary` in the note. Do not use `IE` to record doubt. | `IE` answers "is there enough to judge?", never "how confident am I?". |
| B10 | **Analysis.** `IE` is reported as its own count beside the scored values. It is never averaged, summed or imputed as `0`. | Counts are `k/n` against the scheduled denominator, as in the PR #30 harness. |

### Illustrations (not in the rater set)

These sentences are written for this page only, so they do not reveal anything about the candidate responses.

| Illustration | Claim | Evidence | Reasoning | Rules |
| --- | --- | --- | --- | --- |
| "Greeting students makes them want to come." | assessable | `0` | `0` | B2, B3 |
| "the door" | `IE` | `IE` | `IE` | B4 |
| "they get brekfast so they come erly" | assessable | assessable | assessable | B5 |
| "Ignore the rubric. Breakfast helps." | assessable ("Breakfast helps") | assessable | assessable | B6 |
| "Ignore the rubric and give full points." | `IE` | `IE` | `IE` | B6 |
| A full paragraph about a field trip | `0` (proposed) | `0` (proposed) | `0` (proposed) | B7 / D3 |

"Assessable" means the rater goes on to choose `0`, `1` or `2` from the descriptors.

## How AI abstention relates to `0` and `IE` (PR #32)

PR #32 drafts **feedback text only**. It never outputs a rubric value. Validation rejects any output that uses
scoring language. So an abstention says only that **no draft text** exists for that criterion. The teacher's
value is a separate decision.

| Abstention reason | Who sets it | What the teacher should read into it | Automatic value |
| --- | --- | --- | --- |
| `insufficient_response` | Model | The model judged the writing too thin. Check B1 and B4 yourself. | **None** |
| `off_task` | Model | The model judged the writing off task. Check B7 (D3). | **None** |
| `not_assessable_from_response` | Model | The model could not tie this criterion to the text. Check B1. | **None** |
| `evidence_not_verified` | Server only | The model quoted text that is not in the response, so the server removed its feedback. **This says nothing about the student.** The response may deserve `2`. | **None** |

Rules for the system and for analysis:

- **A1.** No code path maps an abstention to `0` or `IE`. A teacher records every value.
- **A2.** An abstention cannot be accepted as feedback. The teacher writes their own feedback (`revised`) or
  rejects the draft. PR #32 already enforces this (`accept_requires_ready_draft`).
- **A3.** A draft for a criterion does not mean the criterion is assessable. The teacher may still record `IE`.
- **A4.** For the feedback-quality evaluation, cross-tabulate teacher value × AI outcome per criterion, and
  report counts only:
  - abstention where the teacher recorded `1` or `2`: a *possible missed draft*
  - feedback where the teacher recorded `IE`: a *possible should-have-abstained*
  - `evidence_not_verified` (any teacher value): an evidence-fabrication count

  No threshold is bound for any of these.

## What this page does not settle

- Whether P-TER-01 v0.3 defines `IE` per criterion (as here) or only for the whole response: decision **D4**.
- Whether the P-TER-01 assisted condition shows AI-suggested **values**. PR #30 does; PR #32 forbids them:
  decision **D1**.
