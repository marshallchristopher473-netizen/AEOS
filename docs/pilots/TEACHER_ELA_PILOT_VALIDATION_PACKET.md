# AEOS unified teacher ELA workflow pilot — validation packet

**Status:** draft for founder and teacher confirmation. **Data boundary:** synthetic work only; teacher accounts only; no student identifiers or real student work.

## 1. Protocol/asset reconciliation gate

No current P-TER-01 protocol or pilot asset was accessible in the supplied workspace on 2026-10-17. This packet does not recreate, infer, or replace those materials. Before approval, the founder records the authoritative source below and reconciles every blank/source-dependent item.

| Item | Authoritative source/version | Reconciled by/date | Result/notes |
|---|---|---|---|
| P-TER-01 protocol |  |  |  |
| Assignment prompt |  |  |  |
| Approved ELA rubric |  |  |  |
| Pilot workflow/screens |  |  |  |
| Evaluator mode/version |  |  |  |
| Support and escalation contacts |  |  |  |

If reconciliation changes a locked design field below, version this packet and re-approve it before collection.

## 2. Purpose, scope, and non-claims

This is a small feasibility/usability test of the unified teacher ELA review workflow using predefined synthetic responses. It observes whether teachers can complete one review task and where corrections or problems occur. It is **not** a study of learning, diagnostic accuracy, MCAP alignment, rubric validity, or AI quality. It will not support efficacy, causal, or generalizable claims.

This packet separates two activities:

| Activity | Purpose | Inputs | What may be concluded |
|---|---|---|---|
| Synthetic mock usability test | Observe task completion, time, correction burden, issues, and teacher opinion | Synthetic responses only | Descriptive feasibility/usability observations only |
| Live AI review experiment | Compare an actually configured evaluator on an approved corpus against an approved comparator | Not authorized by this packet | Requires separate approved protocol, permissions, data-handling scope, evaluator/version lock, and analysis plan |

No real student work may be entered, uploaded, pasted, or discussed. Any move to real student work requires applicable permissions and a documented data-handling scope established before that move. This template does not itself establish legal compliance.

## 3. Locked feasibility design — approve before outcomes exist

### Participants

Enroll **3–5 teachers**, only after founder and each teacher confirm participation. Assign IDs T01–T05; leave unused IDs blank. Record role/grade band only if voluntarily supplied and non-identifying in reporting.

| Teacher ID | Confirmed (Y/N) | Order | Matched set | Notes |
|---|---:|---|---|---|
| T01 |  | A → B | X → Y |  |
| T02 |  | B → A | Y → X |  |
| T03 |  | A → B | X → Y |  |
| T04 |  | B → A | Y → X |  |
| T05 |  | A → B | X → Y |  |

### Materials to be approved

- **Assignment prompt:** `[insert exact, approved prompt and source/version]`
- **Rubric:** `[insert exact approved rubric title/version and source]`
- **Evaluator used in the mock:** `[mode/model/build/prompt configuration/version or “none”]`. Do not label it an experiment or infer performance unless this exact configuration is documented.
- **Manual comparator:** a named, trained reviewer applies the approved rubric to the same synthetic response using a written answer key/evidence map, before teacher sessions and blinded to task order. Comparator identity/role: `[blank]`; key/evidence-map version: `[blank]`.

### Synthetic response register (6–10 total)

Create and freeze **six synthetic responses per teacher** (the smallest requested 6–10 workload) only after the assignment/rubric are approved. Each teacher reviews matched set X (three responses) in one task and set Y (three responses) in the other. The same six synthetic responses may be reused across teachers, but not across tasks for the same teacher. Sets X and Y should be matched for rubric dimension, intended score band, length, and seeded-error burden. Do not place student-like personal data in them. The four optional rows permit an approved expansion to 7–10 responses per teacher without changing the structure.

| Synthetic ID | SHA-256 hash after freeze | Set | Intended rubric profile | Seeded error(s) / test condition | Comparator key version | Approved (Y/N) |
|---|---|---|---|---|---|---:|
| SYN-01 |  | X |  |  |  |  |
| SYN-02 |  | X |  |  |  |  |
| SYN-03 |  | X |  |  |  |  |
| SYN-04 |  | X |  |  |  |  |
| SYN-05 |  | Y |  |  |  |  |
| SYN-06 |  | Y |  |  |  |  |
| SYN-07 (optional) |  | Y |  |  |  |  |
| SYN-08 (optional) |  | Y |  |  |  |  |
| SYN-09 (optional) |  |  |  |  |  |  |
| SYN-10 (optional) |  |  |  |  |  |  |

Seeded errors are intentionally introduced test conditions, not evidence of an evaluator’s failure. Name only errors justified by the approved rubric/key (for example: score mismatch, unsupported evidence citation, omitted rubric criterion, or incorrect evidence location); leave cells blank until approved. Re-hash/re-approve after any change.

### Task, counterbalancing, and order

Each teacher performs two equivalent review tasks, each containing three assigned synthetic responses:

- **A — assisted workflow:** review the configured workflow output, inspect cited evidence, accept/edit/correct as needed, and submit a final rubric decision.
- **B — manual workflow:** review the matched response without workflow output and submit a final rubric decision using the same rubric.

Use the assigned A→B/B→A order and X→Y/Y→X matched response sets in the participant table. This reduces, but does not eliminate, practice, order, response-set, and expectancy effects. With 3–5 teachers and synthetic responses, results remain descriptive and cannot estimate efficacy, validity, or AI quality.

**Per-task sequence:** facilitator setup → teacher reads task instructions → start timer when the teacher first opens the first assigned response → repeat review/evidence check/final decision/verification/correction for all three assigned responses → stop timer when the teacher says the final entry is complete → short form. Record each response-level outcome and the task total. The facilitator gives no content/rubric coaching beyond scripted clarification.

### Time definition (locked)

**Total active review time** is the elapsed time from first opening the first response in the assigned set to completion of teacher verification and any correction made before the teacher declares the final entry complete. Exclude consent/onboarding, facilitator technical setup, breaks, and post-task survey discussion. Log excluded intervals and reason. Also record a response-level active time using the same rule for each response. Do not compare time across tasks unless both had the same timer rule and no unresolved technical interruption.

### Preselected success thresholds (lock before collection)

Select only approved thresholds below; leave unselected fields blank. Do not fill after outcomes are known.

| Measure | Threshold / decision rule | Selected & locked by/date |
|---|---|---|
| Completion rate |  |  |
| Total active review time |  |  |
| Corrections per completed task |  |  |
| Unresolved errors per completed task |  |  |
| Rubric agreement with comparator |  |  |
| Evidence agreement with comparator |  |  |
| Teacher-reported usefulness |  |  |

## 4. Teacher onboarding and consent/scope script

> You are being invited to try one synthetic ELA-review workflow as a usability/feasibility activity. The materials are fabricated for this activity; do not enter, paste, upload, or discuss student-identifying information or real student work. We will record task completion, active review time, edits/corrections, unresolved issues, agreement with a prewritten manual comparator, and your opinion of usefulness. This activity is not an evaluation of your performance and is not designed to establish AI quality, diagnostic validity, MCAP alignment, learning impact, or legal compliance. Participation is voluntary. You may skip any question, pause, or withdraw without giving a reason. Please do not rely on the workflow output as an authority; use the approved rubric and your own judgment. Support contact: `[name/email or channel]`. Data handling/retention contact: `[name/email or channel]`.

**Confirmation (required before task):** “I understand the synthetic-only scope, voluntary nature, and withdrawal process.” □ Yes  Teacher ID: ___ Date: ___ Facilitator: ___

## 5. Measurement forms

### Facilitator task record (one per task)

Teacher ID: ___  Session ID: ___  Task: A / B  Set: X / Y  Response ID(s): ___ / ___ / ___  Date: ___

| Field | Record |
|---|---|
| Evaluator mode/version actually displayed (A only) |  |
| Task start / stop time |  |
| Excluded interval(s), reason, duration |  |
| Task active review time |  |
| Completed final decision? (Y/N) |  |
| Response-level times, corrections, unresolved errors, final rubric/evidence, comparator result/key, and agreement (one line per response) |  |
| Observed event(s), verbatim when useful |  |
| Technical issue / incident ID |  |

### Teacher post-task form (opinion, not observed performance)

1. I could complete the assigned synthetic review task: □ yes □ no □ partially.
2. Usefulness for this synthetic task: □ not useful □ slightly useful □ moderately useful □ very useful □ extremely useful.
3. What helped or hindered you? ___
4. Was anything inaccurate, unclear, or unresolved? ___
5. Optional: what would you change? ___

## 6. Evidence log (blank)

| Record ID | Date/time | Observer | Type (event/opinion/artifact) | Factual description or exact quote | Linked task/response | Source/location | Follow-up/status |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |

Keep observed events separate from teacher-reported opinion. Do not convert either into claims beyond the recorded evidence.

## 7. Withdrawal, retention/deletion, incident and stop rules

**Withdrawal:** A teacher may tell the facilitator or support contact verbally or in writing at any time. Stop their task immediately, mark their session withdrawn, and do not collect further input. Before de-identification/aggregation, delete their session record and associated notes/logs on request. After de-identified aggregation has been completed, explain whether removal is no longer feasible; record this boundary before participation.

**Retention/deletion:** Store only teacher ID, task records, non-identifying feedback, configuration/version metadata, and synthetic artifact hashes. No real student data. Storage location/access owners: `[blank]`. Retention end date: `[blank]`. At that date, delete raw task records, feedback, exports, recordings (if any), and linkage keys; retain only a non-identifying summary if approved: `[yes/no; details]`. Log deletion date, person, and scope: `[blank]`.

**Incident/stop rules:** Stop the current task; do not continue or troubleshoot with live data if any of the following occurs: attempted real student/personal data entry; wrong evaluator/configuration; unapproved prompt/rubric/response version; unauthorized access/sharing; material safety or privacy concern; or participant distress/withdrawal. Preserve only the minimum non-sensitive incident facts, notify `[owner/contact]`, restrict access, and resume only after documented resolution/re-approval. Incident ID: `[blank]`.

## 8. Analysis and reporting guardrails

Report counts, ranges/medians where useful, task-level completion proportion, active-time definition, correction and unresolved-error counts, comparator agreement rules/results, and verbatim/attributed opinion separately. State missing data and deviations. Describe feasibility descriptively (for example, “3 of 4 participating teachers completed both synthetic tasks under the preselected rule”), never as efficacy or AI-quality proof. Do not pool or compare A/B outcomes as causal evidence in this small counterbalanced mock.

**Comparator agreement rule (must be written before collection):** rubric agreement = `[exact score/dimension rule]`; evidence agreement = `[exact citation/location rule]`; partial = `[rule]`; adjudicator, if used = `[name/role]`.

## 9. Approval block

Founder: ___ Date: ___  Teacher representative/reviewer: ___ Date: ___  Protocol reconciler: ___ Date: ___

