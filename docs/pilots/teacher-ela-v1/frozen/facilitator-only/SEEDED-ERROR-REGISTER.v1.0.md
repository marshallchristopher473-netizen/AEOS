# Seeded-error register v1.0

**FACILITATOR AND COMPARATOR ONLY. Do not show this file to participating teachers.**

Seeded errors are test conditions placed in the MockAssisted-ELA v0.1 output cards on purpose. They are not evidence about any evaluator. Each card has exactly one. Every other field on the card matches KEY-ELA-01.

Error types come only from the packet's approved list: score mismatch, unsupported evidence citation, omitted rubric criterion, incorrect evidence location.

| Error ID | Response | Set | Type | Where on the card | What the card says | Correct final record (KEY-ELA-01) | Counts as resolved when |
|---|---|---|---|---|---|---|---|
| ERR-01 | SYN-01 | X | score mismatch | Suggested scores, Reasoning row | Reasoning 2 (total 11); claims the mowing detail is not explained | Reasoning 3 (total 12); the mowing detail is explained ("solves the problem and costs less") | Final Reasoning score is 3 |
| ERR-02 | SYN-02 | X | unsupported evidence citation | Cited evidence, row E3 | Quotes "it was good for the bees and the environment" as text from the response | The response contains no such text. Evidence is K1 and K2 only | E3 is not in the final evidence record |
| ERR-03 | SYN-03 | X | omitted rubric criterion | Suggested scores, Conventions row missing | No Conventions score; total 4 | Conventions 1 (total 5) | Final record includes Conventions 1 |
| ERR-04 | SYN-04 | Y | score mismatch | Suggested scores, Evidence row (rows E2 and E3 mislabeled "general" to match) | Evidence 2 (total 11) | Evidence 3 (total 12); E2 and E3 are specific | Final Evidence score is 3 |
| ERR-05 | SYN-05 | Y | unsupported evidence citation | Cited evidence, row E3 | Quotes "nature in the city got better" as text from the response | The response contains no such text. Evidence is K1 and K2 only | E3 is not in the final evidence record |
| ERR-06 | SYN-06 | Y | incorrect evidence location | Cited evidence, row E1 | Locates "the bees came back after the strips was planted" in ¶2 | ¶5 (or ¶1, ¶5) | E1 is recorded with ¶5 or ¶1, ¶5 |

## Balance between sets

| | Set X | Set Y |
|---|---|---|
| Seeded errors | 3 (one per response) | 3 (one per response) |
| Score mismatch | 1 (ERR-01, 12-point response) | 1 (ERR-04, 12-point response) |
| Unsupported evidence citation | 1 (ERR-02, 8-point response) | 1 (ERR-05, 8-point response) |
| Third error | omitted rubric criterion (ERR-03, 5-point response) | incorrect evidence location (ERR-06, 5-point response) |

**Known limitation:** the third error differs in type between sets (omitted criterion vs. incorrect location). That gives two of each of the first two types and covers all four approved types. The two may differ in how easy they are to detect. Report unresolved-error results by error type, not only as a set total, and do not read an X–Y difference as an effect of the workflow.

## Recording rule

For each assisted (A) response, the facilitator records the seeded error as **resolved** or **unresolved** from the teacher's final submitted record, using the "Counts as resolved when" column. A teacher who notices an error but does not change the final record leaves it **unresolved**. Record the notice in the evidence log as an observed event.
