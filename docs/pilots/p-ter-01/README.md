# P-TER-01 reconciliation for PR #32 (target: v0.3)

| Field | Value |
| --- | --- |
| Scope | Reconcile the PR #32 feedback-drafting workflow with P-TER-01. Add a separate, unapproved attendance candidate. |
| Status | **Candidate only. Nothing here is approved.** |
| Feature flag | `AEOS_AI_FEEDBACK_ENABLED=false` (default, unchanged) |
| Approval pins | `AEOS_AI_FEEDBACK_APPROVED_RUBRICS` empty (unchanged); `manifest.json` `approval_pins: []` |
| Data | Synthetic authored text only |

## The P-TER-01 v0.3 source was not located

The reconciliation target is P-TER-01 **v0.3**. No copy of it could be found. Searched on 2026-10-12:

| Source | Result |
| --- | --- |
| This repository: every remote branch and every `refs/pull/*/head` (contents and commit messages) | `P-TER-01` appears only in PR #30 (which targets v0.2 and records it as not located) and PR #32. No `v0.3`, no attendance task. |
| Google Drive (full-text search: `P-TER-01`, `P-TER`, `attendance`, `abstention`) | Mentioned only in *AEOS Claude Ultracode Prompt Pack v0.1*. No protocol file. |
| Notion (`P-TER-01`) | No match |

So **nothing in this folder is transcribed from v0.3**. The attendance task, its rubric and the boundary rules are
newly written candidates, labelled with the target version `0.3`. They must be checked against the v0.3 packet
once someone supplies it. Until then the protocol is recorded as `SOURCE_NOT_LOCATED` in `manifest.json`, and
every comparison below is against what the repository actually contains: PR #30 (the v0.1 preparation harness)
and PR #32.

## Contents

| Path | What it is | Status |
| --- | --- | --- |
| [`SCORING_BOUNDARIES.md`](SCORING_BOUNDARIES.md) | Rules that separate `0`, `IE` and AI abstention, with checks and illustrations | CANDIDATE-UNAPPROVED |
| [`REVIEW_WORKSHEET.md`](REVIEW_WORKSHEET.md) | Human review: blind scoring, descriptor review, rule dispositions, open decisions D1–D5, sign-off | Blank template |
| `candidates/attendance/task.TASK-ATTEND.v0.3.candidate.json` | Fictional passage *The Morning Check-In*, prompt, 8 unlabeled synthetic responses | CANDIDATE-UNAPPROVED |
| `candidates/attendance/rubric.RUB-ATTEND3.v0.3.candidate.json` | Claim / Evidence / Reasoning rubric with explicit `0` and `IE` definitions | CANDIDATE-UNAPPROVED |
| [`manifest.json`](manifest.json) | sha256 of every candidate file and every preserved fixture; empty approval pins; open gates | Current |
| `backend/tests/test_pter01_candidate.py` | Guards: candidate not loadable, flag off, pins empty, fixtures unchanged, hashes match | Passing |

The candidate sits **outside** `backend/app/services/ai_feedback/rubrics/`, so the server cannot load it. Even if
someone pinned its hash, the server would return `rubric_not_found`. A test enforces this.

No answer key is committed. The responses are unlabeled so that Part B of the worksheet is blind scoring.

## Preserved engineering fixtures

These files are unchanged byte for byte. `test_pter01_candidate.py` pins their sha256.

| Path | Role | sha256 |
| --- | --- | --- |
| `backend/app/services/ai_feedback/rubrics/RUB-CER3.v0.1.json` | PR #32 server rubric (PROPOSED-UNREVIEWED, unpinned) | `8dbec68e…` |
| `backend/tests/fixtures/ai_feedback/synthetic_ela.json` | PR #32 workflow test fixtures (cool roofs, labelled profiles, injection cases) | `97f534a3…` |

RUB-CER3's canonical pin hash is still `8f7584b2…`, which is the value shown in `docs/AI_FEEDBACK_DRAFTING.md`.
These are **engineering fixtures**: their response profiles are labelled, so they cannot serve as a blind rater set.

## Reconciliation: PR #32 against P-TER-01 (as recorded in PR #30)

| # | Element | PR #30 (P-TER-01 prep) | PR #32 | Status |
| --- | --- | --- | --- | --- |
| R1 | Protocol | v0.2, SOURCE_NOT_LOCATED | none | **OPEN.** Target is now v0.3, also not located. |
| R2 | Rubric | RUB-CER3@0.1, PROPOSED-UNREVIEWED | Same content, copied with provenance | Consistent. Unchanged here. |
| R3 | Values `0`/`1`/`2`/`IE` | AI-drafted values with spans in the assisted condition | The AI never outputs values; scoring language is rejected | **CONFLICT → D1** |
| R4 | `IE` meaning | One-line note: "too incomplete to judge" | Not used | Clarified in `SCORING_BOUNDARIES.md` (B1–B10). Pending review. |
| R5 | Abstention | No concept | Per-criterion `abstain` with four reasons; server-only `evidence_not_verified` | Separated from `0`/`IE` (A1–A4). No mapping exists in code. |
| R6 | Evidence spans | Required for `1`/`2`, forbidden for `0`/`IE` | Server locates quotes verbatim (≥ 8 chars); spans support feedback, not values | Compatible. B8 restates the PR #30 rule. |
| R7 | Accept / revise / reject | Per criterion (`criteria.csv`) | Per whole draft (API, append-only) | **Granularity differs → D2** |
| R8 | Off-topic responses | Not defined | `off_task` reason and `off_topic` flag | Proposed `0` (B7) → **D3** |
| R9 | `IE` scope | Per criterion | n/a | Per criterion proposed → **D4** |
| R10 | Measures (setup, active review, pause/repair, abandonment) | Offline tables | Not captured | Not reconciled. A P-TER-01 run would use the PR #30 tables. |
| R11 | Data classification | Synthetic only | `CHECK (data_classification = 'synthetic')` | Consistent |
| R12 | Approval | Independent reviewer disposition | Hash pin in server config | Consistent. Both still open. |

### Engineering fix found during reconciliation

PR #32's head `2674540` **does not import**: `app.models.ai_feedback` was never committed, because the root
`.gitignore` rule `models/` also matched `backend/app/models/`. PR #32's 521-passing result was presumably produced on a
working tree that still held the untracked file. A clean checkout of `2674540` fails with `ModuleNotFoundError`. Commit `ed10dc9` on this branch:

- reconstructs the module from its callers, its tests and the documented contract
- re-includes `backend/app/models/` in `.gitignore`

The reconstruction passes the full existing suite. It is a reconstruction, though, not the original file, so
reviewers should read it.

## Remaining gates (blocking)

| Gate | Status | Closes when |
| --- | --- | --- |
| P-TER-01 v0.3 source | OPEN (SOURCE_NOT_LOCATED) | The packet is supplied, bound by sha256 in `manifest.json`, and R1–R12 are re-checked against it |
| Owner decisions D1–D5 | OPEN | Recorded on the worksheet with who decided |
| Independent review of the attendance candidate | OPEN | Worksheet Part F is complete with APPROVE for every artifact |
| Adjudicated key for TASK-ATTEND | OPEN | At least two blind Part B scorings are adjudicated. The key is stored outside the public repository. |
| RUB-CER3 approval (PR #32) | OPEN | Unchanged from PR #32 |
| Review of the reconstructed `app/models/ai_feedback.py` | OPEN | A human confirms it matches the intended contract |
| Provider smoke check, quality evaluation, filter false-rejection rate, CI on an exact head, hosted DB gate, consent / data agreement | OPEN | Unchanged from PR #32 |

## Not done, by instruction

The feature flag was not turned on. No approval pin was set anywhere. No rubric was added to the server
registry. No engineering fixture was edited. No score, key or reviewer response was created. No real student data
was used.
