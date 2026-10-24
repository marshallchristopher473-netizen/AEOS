# Evaluator specification: MockAssisted-ELA v0.1

## What it is

MockAssisted-ELA v0.1 is a **scripted, deterministic stand-in** for an assisted-review workflow. It is the six pre-written output cards in `frozen/outputs/` (one per synthetic response). Nothing is generated during a session.

| Property | Value |
|---|---|
| Mode | Pre-written document cards. No software, model, API, prompt, or network call. |
| Live inference | None. No AI model produces or alters any output during the pilot. |
| Determinism | Every teacher sees byte-identical cards. The SHA-256 of each card is in `FREEZE_MANIFEST.sha256`. |
| Inputs | Assignment A v1.0, AEOS Mock ELA Rubric v1.0, and the matching synthetic response. |
| Output per response | A suggested score for each rubric dimension with a short rationale, a suggested total, and a table of evidence quoted from the response with passage locations and labels. |
| Seeded errors | Exactly one per card, recorded in `frozen/facilitator-only/SEEDED-ERROR-REGISTER.v1.0.md`. Every other field matches KEY-ELA-01. |
| Version label shown to teachers | "MockAssisted-ELA v0.1 (pre-written for this activity; not produced by AI)" |

## What it may and may not be used to conclude

- It **may** support descriptive observations about whether teachers can review a workflow-style output, check its evidence, catch and correct its mistakes, and complete a final rubric decision.
- It **may not** support any statement about the accuracy, quality, reliability, speed, or safety of any AI model, AEOS evaluator, or future product. The cards were written by hand to a key, and their error rate was chosen in advance (one per card).
- Do not call results from this mock an "AI evaluation", "experiment", or "model performance". The packet's live-AI row (§2) stays not authorized.

## Change control

Any edit to a card, including fixing a typo, creates a new evaluator version (v0.2). The new version needs a new hash and packet re-approval before collection (packet §7). Showing teachers a card whose hash does not match the manifest is a stop condition.
