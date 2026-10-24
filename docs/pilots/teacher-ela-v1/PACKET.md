# AEOS unified teacher ELA workflow pilot: validation packet v1.0

**Status:** v1.0, content frozen 2026-10-24. **Collection gate: BLOCKED** until every `FOUNDER-TO-RECORD` item in §1, §3, §4 and §7 is filled and §9 is signed.
**Data boundary:** synthetic work only; teacher accounts only; no student identifiers or real student work.
**Audience:** founder, facilitator, comparator. This file contains the seeded-error register and key references. Do not give it to participating teachers.
**Template source:** `docs/pilots/TEACHER_ELA_PILOT_VALIDATION_PACKET.md` from draft PR #36 at `e7f6a57`. Section numbers match it, and §3a is added.

## 0. Packet contents and freeze

Every asset is a separate file so its bytes can be hashed. `FREEZE_MANIFEST.sha256` lists the SHA-256 of every file under `frozen/` and of this `PACKET.md`. Two ways to verify:

```bash
cd docs/pilots/teacher-ela-v1
sha256sum -c FREEZE_MANIFEST.sha256        # byte-level freeze check
python3 -I verify_packet.py                 # freeze + design, key, card and register consistency
```

| Asset | File | Teacher-facing? | SHA-256 |
|---|---|---|---|
| Assignment prompt and passage | `frozen/A-assignment-prompt.v1.0.md` | Yes | `59c388c554c5e7b448863e1b6a57844c0f48220ca9f225f1b71992cceb6ae702` |
| AEOS Mock ELA Rubric v1.0 | `frozen/B-rubric.AEOS-MOCK-ELA.v1.0.md` | Yes | `9318eb9444bf2aaf572e941083cc2196399b0c63755093dfc625506fdba57b23` |
| Evaluator spec: MockAssisted-ELA v0.1 | `frozen/C-evaluator-spec.MockAssisted-ELA.v0.1.md` | No | `75afcacd18423f10f5b4e5a0d16bca92d65b202406dfc6b4be1d0ed88d8f7ad4` |
| Task instructions and final decision sheet | `frozen/D-task-instructions.v1.0.md` | Yes | `7ed77bf0919d617bdfb10729c1a938cefeead3c86163e4f2f4d0e0da88c656af` |
| Synthetic responses SYN-01 to SYN-06 | `frozen/responses/SYN-0N.md` | Yes | see §3 register |
| Workflow output cards (Task A only) | `frozen/outputs/SYN-01.output.md` | Yes | `ec58b3739672a26a2358a14e629705dc1b9ca6d53d54547967c415fc808b4fc2` |
|  | `frozen/outputs/SYN-02.output.md` | Yes | `fc2b05c0aa8d96170ad5ddee45c652acc320d08b9c50a929b34813d628310062` |
|  | `frozen/outputs/SYN-03.output.md` | Yes | `ac79634f27605557cf28ddf0e1c501d1fea98e161dac4ac95c9aae3e97389aac` |
|  | `frozen/outputs/SYN-04.output.md` | Yes | `916ee375fcb786799a652db4ff38be2f28e1c72fff6e0f4c1e13e5314f575264` |
|  | `frozen/outputs/SYN-05.output.md` | Yes | `eb8a0eb01259ea9dfb763e471620223b3412704907b62f09e4a921ffefb27879` |
|  | `frozen/outputs/SYN-06.output.md` | Yes | `09081e5ca4efa8e47b621668babfeda43848e9ee64398e2b595454d9d32b2b14` |
| Comparator answer key KEY-ELA-01 v1.0 | `frozen/facilitator-only/KEY-ELA-01.md` | **No** | `9c007dcfe3f83ec9d772e1c6c29041f3c5ba7db36fffb1e017501bd1f2e41dbf` |
| Seeded-error register v1.0 | `frozen/facilitator-only/SEEDED-ERROR-REGISTER.v1.0.md` | **No** | `fb7ea73154311084dd2788ab4f556e78f9e0f580829e021985de36bf3474b996` |

This file's own hash cannot appear inside it. It is in `FREEZE_MANIFEST.sha256`, and §9 records the manifest's hash at signing.

## 1. Protocol/asset reconciliation gate

On 2026-10-24 the AEOS repository's `main` branch (`b9c68aa`) still contained no P-TER-01 protocol, assignment prompt, ELA rubric, evaluator configuration, or teacher ELA review workflow/screens. Related work is unmerged and unapproved, in open draft pull requests: #23 teacher assessment review workflow, #30 offline synthetic P-TER-01 review harness, #32 AI feedback drafting on synthetic ELA responses, #35 P-TER-01 reconciliation for #32, #36 this packet's template, #47/#50 AI feedback pilot consolidation. None of it is an approved source for this packet.

To avoid depending on unapproved work, v1.0 supplies its own synthetic materials (§0). They are self-contained and do not reproduce or infer any P-TER-01 content. If the founder records a P-TER-01 version whose prompt, rubric, or evaluator differs from these, version this packet (v1.1), re-hash, and re-approve before collection.

| Item | Authoritative source/version | Reconciled by/date | Result/notes |
|---|---|---|---|
| P-TER-01 protocol | `FOUNDER-TO-RECORD` (source and version, or "not used for this pilot") | `FOUNDER-TO-RECORD` | Candidate drafts exist only in open PRs #30 and #35. Not approved. |
| Assignment prompt | This packet: `frozen/A-assignment-prompt.v1.0.md` | Packet author, 2026-10-24; founder confirms at §9 | Original fictional passage, 5 paragraphs, with a constructed-response task. |
| Approved ELA rubric | This packet: `frozen/B-rubric.AEOS-MOCK-ELA.v1.0.md` (AEOS Mock ELA Rubric v1.0) | Packet author, 2026-10-24; founder confirms at §9 | Analytic, 4 dimensions × 0–3, total 0–12. Not validated or aligned to any state assessment. |
| Pilot workflow/screens | Document-based mock: response + output card + final decision sheet (`frozen/D-…`, `frozen/outputs/`) | Packet author, 2026-10-24; founder confirms at §9 | No software screens. The cards can be printed or opened read-only. See §3a D4. |
| Evaluator mode/version | MockAssisted-ELA v0.1: scripted, deterministic, no live inference (`frozen/C-…`) | Packet author, 2026-10-24; founder confirms at §9 | Supports no AI-quality claim (§2). |
| Support and escalation contacts | `FOUNDER-TO-RECORD` | `FOUNDER-TO-RECORD` | Also needed in §4 and §7. |

If reconciliation changes a locked design field below, version this packet and re-approve it before collection.

## 2. Purpose, scope, and non-claims

This is a small feasibility/usability test of the unified teacher ELA review workflow using predefined synthetic responses. It observes whether teachers can complete one review task and where corrections or problems occur. It is **not** a study of learning, diagnostic accuracy, MCAP alignment, rubric validity, or AI quality. It will not support efficacy, causal, or generalizable claims.

This packet separates two activities:

| Activity | Purpose | Inputs | What may be concluded |
|---|---|---|---|
| Synthetic mock usability test | Observe task completion, time, correction burden, issues, and teacher opinion | Synthetic responses only, with MockAssisted-ELA v0.1 cards | Descriptive feasibility/usability observations only |
| Live AI review experiment | Compare an actually configured evaluator on an approved corpus against an approved comparator | Not authorized by this packet | Requires separate approved protocol, permissions, data-handling scope, evaluator/version lock, and analysis plan |

No real student work may be entered, uploaded, pasted, or discussed. Any move to real student work requires applicable permissions and a documented data-handling scope established before that move. This template does not itself establish legal compliance.

## 3. Locked feasibility design: approved before outcomes exist

### Participants

Enroll **3–5 teachers**, only after the founder and each teacher confirm participation. Assign IDs T01–T05; leave unused IDs blank. Record role/grade band only if the teacher volunteers it and it stays non-identifying in reporting.

| Teacher ID | Confirmed (Y/N) | Order | Matched set | Notes |
|---|---:|---|---|---|
| T01 |  | A → B | X → Y |  |
| T02 |  | B → A | X → Y |  |
| T03 |  | A → B | Y → X |  |
| T04 |  | B → A | Y → X |  |
| T05 |  | A → B | X → Y |  |

Resulting set per condition: T01 A=X, T02 A=Y, T03 A=Y, T04 A=X, T05 A=X. T01–T04 form a complete 2×2 rotation so that order and response set are each balanced across conditions; T05 repeats T01. Do not pair the order and set columns in lockstep (A→B always with X→Y, B→A always with Y→X), because that assigns set X to the assisted task for every teacher and makes condition and response set inseparable. Enroll in ID order. With 3 teachers (T01–T03), A=X once and A=Y twice. Report this imbalance.

### Materials (locked)

- **Assignment prompt:** "The City That Plants for Bees", Assignment A v1.0, `frozen/A-assignment-prompt.v1.0.md`. An original fictional informational passage (¶1–¶5) with the task: *"Was Marrowfield's plan a good idea? Write one or two paragraphs. State a clear claim, support it with at least two details from the passage, and explain how each detail supports your claim."*
- **Rubric:** AEOS Mock ELA Rubric v1.0, `frozen/B-rubric.AEOS-MOCK-ELA.v1.0.md`. Analytic: Claim, Evidence, Reasoning, Conventions, each 0–3; total 0–12.
- **Evaluator used in the mock:** MockAssisted-ELA v0.1, `frozen/C-evaluator-spec.MockAssisted-ELA.v0.1.md`. Six pre-written, deterministic output cards; no model, prompt, API, or network; no live inference. Each card carries exactly one seeded error and is otherwise identical to the key. Not an experiment, and no performance may be inferred from it.
- **Manual comparator:** a named, trained reviewer applies the approved rubric to every synthetic response *before* teacher sessions, blinded to task order, then checks the result against written key KEY-ELA-01 v1.0 (`frozen/facilitator-only/KEY-ELA-01.md`). Any disagreement with the key is a stop condition (§7). Comparator identity/role: `FOUNDER-TO-RECORD`. Key/evidence-map version: **KEY-ELA-01 v1.0**.

### Synthetic response register (6 used)

Six synthetic responses are frozen and used by every teacher. Each teacher reviews matched set X (three responses) in one task and set Y (three responses) in the other. The same six responses are reused across teachers, never across tasks for the same teacher. Sets are matched pair by pair (SYN-01↔SYN-04, SYN-02↔SYN-05, SYN-03↔SYN-06) on exact rubric profile, length (within 10%), and seeded-error burden (one error per response). They contain no student-like personal data. The four optional rows stay unused. Any expansion must keep X and Y the same size (8 or 10 total), changes the three-responses-per-task count below, and requires a versioned, re-approved packet before collection.

| Synthetic ID | SHA-256 hash after freeze | Set | Intended rubric profile | Seeded error(s) / test condition | Comparator key version | Approved (Y/N) |
|---|---|---|---|---|---|---:|
| SYN-01 | `1b0b6ef489ffac76ec610eb5520e0f2ea6f1e61c310e6984cc26b0afa86e5823` | X | C3 E3 R3 V3 = 12 (129 words) | ERR-01 score mismatch: card suggests Reasoning 2 | KEY-ELA-01 v1.0 | pending §9 |
| SYN-02 | `48a791d4755b49038c8ee4801b208be3c00da3a5fb341ebd68938e8e9154dd9f` | X | C2 E2 R2 V2 = 8 (62 words) | ERR-02 unsupported evidence citation: card row E3 quotes text not in the response | KEY-ELA-01 v1.0 | pending §9 |
| SYN-03 | `653ece98544e2519ec034d7dbfd873639a034d10dc55e5a60c477522b2681516` | X | C2 E1 R1 V1 = 5 (38 words) | ERR-03 omitted rubric criterion: card has no Conventions score | KEY-ELA-01 v1.0 | pending §9 |
| SYN-04 | `fa892b1efdd9e929dbd17f2836edf07364df27c43171c7b0d4e024d4afacdcb5` | Y | C3 E3 R3 V3 = 12 (137 words) | ERR-04 score mismatch: card suggests Evidence 2 | KEY-ELA-01 v1.0 | pending §9 |
| SYN-05 | `69dd9bdc9b9ed524e2a87e1109038be83078c4222069b5d9c376c08b15e833c6` | Y | C2 E2 R2 V2 = 8 (67 words) | ERR-05 unsupported evidence citation: card row E3 quotes text not in the response | KEY-ELA-01 v1.0 | pending §9 |
| SYN-06 | `bbf3f451b5adca2ffdb08c2b08ddd9a9e46a38d4a18ee203622fb4b4e7be373b` | Y | C2 E1 R1 V1 = 5 (40 words) | ERR-06 incorrect evidence location: card puts row E1 in ¶2 (key: ¶5) | KEY-ELA-01 v1.0 | pending §9 |
| SYN-07 (optional) |  |  |  | not used in v1.0 |  |  |
| SYN-08 (optional) |  |  |  | not used in v1.0 |  |  |
| SYN-09 (optional) |  |  |  | not used in v1.0 |  |  |
| SYN-10 (optional) |  |  |  | not used in v1.0 |  |  |

Seeded errors are intentionally introduced test conditions, not evidence of an evaluator's failure. All six come from the approved list. Two are score mismatches, two unsupported evidence citations, one an omitted rubric criterion, and one an incorrect evidence location, so each set has three different types. The full register, including the X/Y type-balance limitation, is `frozen/facilitator-only/SEEDED-ERROR-REGISTER.v1.0.md`. Re-hash/re-approve after any change.

### Task, counterbalancing, and order

Each teacher performs two equivalent review tasks, each containing three assigned synthetic responses:

- **A — assisted workflow:** review the MockAssisted-ELA output card, inspect cited evidence, accept/edit/correct as needed, and submit a final rubric decision on the final decision sheet.
- **B — manual workflow:** review the matched response without workflow output and submit a final rubric decision using the same rubric and sheet.

The facilitator reads the scripted instructions in `frozen/D-task-instructions.v1.0.md` word for word. Use the assigned A→B/B→A order and X→Y/Y→X matched response sets in the participant table. Within a set, present responses in ID order (for example SYN-01, SYN-02, SYN-03). This reduces, but does not eliminate, practice, order, response-set, and expectancy effects. With 3–5 teachers and synthetic responses, results remain descriptive and cannot estimate efficacy, validity, or AI quality.

**Per-task sequence:** facilitator setup → teacher reads task instructions → start timer when the teacher first opens the first assigned response → repeat review/evidence check/final decision/verification/correction for all three assigned responses → stop timer when the teacher says the final entry is complete → short form. Record each response-level outcome and the task total. The facilitator gives no content/rubric coaching beyond scripted clarification.

### Time definition (locked)

**Total active review time** is the elapsed time from first opening the first response in the assigned set to completion of teacher verification and any correction made before the teacher declares the final entry complete. Exclude consent/onboarding, facilitator technical setup, breaks, and post-task survey discussion. Log excluded intervals and reason. Also record a response-level active time using the same rule for each response. Do not compare time across tasks unless both had the same timer rule and no unresolved technical interruption.

### Preselected success thresholds (locked before collection)

These thresholds were set on 2026-10-24, before any session, enrollment, or outcome existed. They may not be edited once any outcome exists. A change before collection requires v1.1 and re-approval.

| Measure | Threshold / decision rule | Selected & locked by/date |
|---|---|---|
| Completion rate | At least 80% of enrolled teachers (rounded up) complete **both** tasks with a submitted final decision for all three responses in each: 3 enrolled → 3; 4 → 4; 5 → 4. | Locked in v1.0 on 2026-10-24, before any outcome; founder ratifies at §9 |
| Total active review time | Median task active review time is **10–30 minutes inclusive**, computed separately for A and for B (three responses per task). Tasks with an unresolved technical interruption are excluded and reported. This is a feasibility band, not a speed or time-saving claim. | Locked in v1.0 on 2026-10-24, before any outcome; founder ratifies at §9 |
| Corrections per completed task | Assisted (A) tasks only: median **≤ 3** corrections per completed task, using the definition in `frozen/D-task-instructions.v1.0.md`. Each A task holds three seeded errors, so 3 is what a teacher who corrects every seeded error and nothing else would record. More than 3 signals corrections beyond the seeded errors. | Locked in v1.0 on 2026-10-24, before any outcome; founder ratifies at §9 |
| Unresolved errors per completed task | **Safety threshold.** **0** unresolved seeded errors across all completed A tasks, per the register's "counts as resolved when" rule. Any single unresolved seeded error fails this threshold and is reported by response and error type. | Locked in v1.0 on 2026-10-24, before any outcome; founder ratifies at §9 |
| Rubric agreement with comparator | At least **2/3** of response-level final decisions in completed A tasks meet the rubric agreement rule (§8). B results are reported descriptively under the same rule. No A–B comparison. | Locked in v1.0 on 2026-10-24, before any outcome; founder ratifies at §9 |
| Evidence agreement with comparator | At least **2/3** of response-level final decisions in completed A tasks meet the evidence agreement rule (§8). B results are reported descriptively under the same rule. No A–B comparison. | Locked in v1.0 on 2026-10-24, before any outcome; founder ratifies at §9 |
| Teacher-reported usefulness | At least **3** teachers rate Task A "moderately useful" or higher on post-task question 2. | Locked in v1.0 on 2026-10-24, before any outcome; founder ratifies at §9 |

**Pilot decision rule (locked):**

| Result | Decision |
|---|---|
| All seven thresholds met | Feasibility signal met. Next gate: write a separate protocol for a live-evaluator experiment (§2). This result is not evidence of AI quality or efficacy. |
| Unresolved-errors safety threshold failed | Do not advance. Revise how the workflow shows evidence and scores, then re-run this mock (new version). |
| Any other threshold failed, or completion below threshold | Do not advance. Record the failure reasons from the evidence log, revise, and re-run. |

## 3a. Deviations from the template (recorded before approval)

| ID | Template text | v1.0 | Reason |
|---|---|---|---|
| D1 | The first supplied template (`b62e556`) put SYN-01–SYN-04 in set X, which implies four X rows. The corrected template (`2066793`, PR #36) splits 3/3. | 3 responses per set (X = SYN-01–03, Y = SYN-04–06). | Follows the locked three-responses-per-task rule. Optional rows SYN-07–10 are unused. |
| D2 | §4 script says only "do not rely on the workflow output as an authority". | Adds that the output was written ahead of time, is not produced by AI, and may contain mistakes. The same sentence is in the Task A instructions. | Scripted cards must not be presented as AI output. The number and type of seeded errors stay undisclosed. |
| D3 | §7 stop rules. | Adds two stop conditions: hash mismatch on any frozen asset, and comparator disagreement with KEY-ELA-01. | Protects the freeze and the comparator reference. |
| D4 | "Pilot workflow/screens" assumed software screens. | Document-based mock: response + output card + final decision sheet. | No approved workflow is on `main` (§1). A document mock is the smallest version that tests the review behaviour. |

## 4. Teacher onboarding and consent/scope script

> You are being invited to try one synthetic ELA-review workflow as a usability/feasibility activity. The materials are fabricated for this activity; do not enter, paste, upload, or discuss student-identifying information or real student work. We will record task completion, active review time, edits/corrections, unresolved issues, agreement with a prewritten manual comparator, and your opinion of usefulness. This activity is not an evaluation of your performance and is not designed to establish AI quality, diagnostic validity, MCAP alignment, learning impact, or legal compliance. Participation is voluntary. You may skip any question, pause, or withdraw without giving a reason. In one task you will see workflow output that was written ahead of time for this activity; it is not produced by AI and it may contain mistakes. Please do not rely on the workflow output as an authority; use the approved rubric and your own judgment. Support contact: `FOUNDER-TO-RECORD (name and email or channel)`. Data handling/retention contact: `FOUNDER-TO-RECORD (name and email or channel)`.

**Confirmation (required before task):** "I understand the synthetic-only scope, voluntary nature, and withdrawal process." □ Yes  Teacher ID: ___ Date: ___ Facilitator: ___

## 5. Measurement forms

### Facilitator task record (one per task)

Teacher ID: ___  Session ID: ___  Task: A / B  Set: X / Y  Response ID(s): ___ / ___ / ___  Date: ___
Manifest check before the session: `sha256sum -c FREEZE_MANIFEST.sha256` result: □ all OK □ mismatch → stop (§7)

| Field | Record |
|---|---|
| Evaluator mode/version actually displayed (A only) | Expected: MockAssisted-ELA v0.1 |
| Task start / stop time |  |
| Excluded interval(s), reason, duration |  |
| Task active review time |  |
| Completed final decision? (Y/N) |  |
| Response-level times, corrections, unresolved errors, final rubric/evidence, comparator result/key, and agreement (one line per response) | Per response: time; corrections (A only); seeded error resolved/unresolved (A only); final C/E/R/V; rubric agreement Y/partial/N; evidence agreement Y/partial/N; key KEY-ELA-01 v1.0 |
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

**Withdrawal:** A teacher may tell the facilitator or support contact verbally or in writing at any time. Stop their task immediately, mark their session withdrawn, and do not collect further input. Before de-identification/aggregation, delete their session record and associated notes/logs on request. Aggregation happens only after the last session. Until then, deletion on request is always possible. After aggregation, a withdrawn teacher's contribution to aggregate counts cannot be separated out; their raw records are still deleted on request. Planned aggregation date: `FOUNDER-TO-RECORD`. Tell teachers about this boundary in onboarding.

**Retention/deletion:** Store only teacher ID, task records, non-identifying feedback, configuration/version metadata, and synthetic artifact hashes. No real student data. Storage location/access owners: `FOUNDER-TO-RECORD`. Retention end date: `FOUNDER-TO-RECORD`. At that date, delete raw task records, feedback, exports, recordings (if any), and linkage keys; retain only a non-identifying summary if approved: `FOUNDER-TO-RECORD (yes/no; details)`. Log deletion date, person, and scope: `[completed at deletion]`.

**Incident/stop rules:** Stop the current task; do not continue or troubleshoot with live data if any of the following occurs:

- attempted real student/personal data entry;
- wrong evaluator/configuration;
- unapproved prompt/rubric/response version;
- **any frozen asset whose SHA-256 does not match `FREEZE_MANIFEST.sha256`** (check before every session);
- **the comparator's independent scores disagree with KEY-ELA-01** on any dimension or required evidence item (checked before the first session);
- unauthorized access/sharing;
- material safety or privacy concern;
- participant distress/withdrawal.

Preserve only the minimum non-sensitive incident facts, notify `FOUNDER-TO-RECORD (owner/contact)`, restrict access, and resume only after documented resolution/re-approval. Incident ID: `[assigned per incident]`.

## 8. Analysis and reporting guardrails

Report counts, ranges/medians where useful, task-level completion proportion, active-time definition, correction and unresolved-error counts, comparator agreement rules/results, and verbatim/attributed opinion separately. State missing data and deviations. Describe feasibility descriptively (for example, "3 of 4 participating teachers completed both synthetic tasks under the preselected rule"), never as efficacy or AI-quality proof. Do not pool or compare A/B outcomes as causal evidence in this small counterbalanced mock.

**Planned descriptive analysis (locked):**

1. Enrollment, withdrawals, and completion against the §3 completion threshold.
2. Median and range of task active review time, separately for A and for B, against the 10–30-minute band.
3. Task A: corrections per completed task (median, range) and the number of seeded errors resolved and unresolved, **by error type and by response**.
4. Rubric and evidence agreement: counts of agree / partial / disagree for A against the 2/3 thresholds; the same counts for B, descriptive only.
5. Post-task usefulness ratings per task, as counts per category; quote free-text answers verbatim and attributed by teacher ID.
6. Every threshold reported as met / not met with the numbers behind it, then the §3 decision rule applied as written.

**Required reporting sentence:** "This was a synthetic, document-based usability mock with pre-written workflow output (MockAssisted-ELA v0.1). It does not measure AI quality, rubric validity, learning, or efficacy, and its A/B results are not causal."

**Comparator agreement rule (written before collection):**

- **Rubric agreement** = all four dimension scores on the final decision sheet exactly match KEY-ELA-01. Because the total is the sum, it matches too.
- **Evidence agreement** = all three of:
  - (a) every `required` key item is recorded with one of its accepted locations;
  - (b) no recorded item is a quotation the response does not contain;
  - (c) every `must be marked not credited` item is recorded as not credited.

  `optional` key items and extra accurate details from the response neither help nor hurt. A close paraphrase of a key item counts as that item.
- **Partial** = rubric: 2 or 3 of the four dimensions match exactly; evidence: at least one but not all of (a)–(c) is satisfied. Partial is reported separately and counts as **non-agreement** for the thresholds.
- **Adjudicator, if used** = none. The comparator's confirmed key is the reference. Disagreements are reported, not resolved after the fact.

## 9. Approval block

Founder: ___ Date: ___  Teacher representative/reviewer: ___ Date: ___  Protocol reconciler: ___ Date: ___

SHA-256 of `FREEZE_MANIFEST.sha256` at signing: ___ (run `sha256sum FREEZE_MANIFEST.sha256`)

Comparator confirmation of KEY-ELA-01 v1.0 completed (all six match): □ Yes  Comparator: ___ Date: ___

Approval confirms §1 reconciliation, the §3 materials, register and thresholds, the §3a deviations, and the `FOUNDER-TO-RECORD` entries. Signatures are recorded on a copy outside this frozen file. Editing this file changes its hash in the manifest.
