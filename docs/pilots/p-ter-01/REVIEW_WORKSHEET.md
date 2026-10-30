# P-TER-01 human review worksheet: attendance candidate

Use this worksheet to review `TASK-ATTEND@0.3`, `RUB-ATTEND3@0.3` and the [scoring boundaries](SCORING_BOUNDARIES.md).
All three are **CANDIDATE-UNAPPROVED**. Nothing here is approved until Part F is complete and signed by a human
reviewer.

**Do not write in the committed copy.** Copy this file to private storage, fill in the copy, and record only its
sha256 and the disposition in the repository. Use a pseudonymous reviewer ID.

Files under review (sha256 values are in [`manifest.json`](manifest.json)):

- `candidates/attendance/task.TASK-ATTEND.v0.3.candidate.json`
- `candidates/attendance/rubric.RUB-ATTEND3.v0.3.candidate.json`
- `SCORING_BOUNDARIES.md`

Stopping points: you can stop after any part. Each part is complete on its own.

---

## Part A: reviewer (5 minutes)

| Field | Entry |
| --- | --- |
| Reviewer ID (pseudonymous) | |
| Qualification (for example, Grade 6–8 ELA teacher, years) | |
| Date | |
| Manifest sha256 you reviewed against | |
| Did you author any of these files? (yes/no) | |
| Have you seen an answer key for this set? (yes/no) | |
| Have you read the AI-authored provenance notes? (yes/no) | |

If you authored the files or have seen a key, you may still do Parts C–E, but Part B does not count as independent
scoring.

## Part B: blind scoring (20–30 minutes)

Score before reading Parts C and D, using only the passage, the prompt and the rubric. Use `0`, `1`, `2` or `IE`.
For `1` or `2`, copy the exact words from the response that show it (B8). Leave nothing blank: if you cannot
decide, choose a value and write `boundary` in the note (B9).

| Response | Criterion | Value | Evidence words (for `1`/`2` only) | Rule(s) used | Note |
| --- | --- | --- | --- | --- | --- |
| A01 | C1 Claim | | | | |
| A01 | C2 Evidence | | | | |
| A01 | C3 Reasoning | | | | |
| A02 | C1 Claim | | | | |
| A02 | C2 Evidence | | | | |
| A02 | C3 Reasoning | | | | |
| A03 | C1 Claim | | | | |
| A03 | C2 Evidence | | | | |
| A03 | C3 Reasoning | | | | |
| A04 | C1 Claim | | | | |
| A04 | C2 Evidence | | | | |
| A04 | C3 Reasoning | | | | |
| A05 | C1 Claim | | | | |
| A05 | C2 Evidence | | | | |
| A05 | C3 Reasoning | | | | |
| A06 | C1 Claim | | | | |
| A06 | C2 Evidence | | | | |
| A06 | C3 Reasoning | | | | |
| A07 | C1 Claim | | | | |
| A07 | C2 Evidence | | | | |
| A07 | C3 Reasoning | | | | |
| A08 | C1 Claim | | | | |
| A08 | C2 Evidence | | | | |
| A08 | C3 Reasoning | | | | |

Time spent on Part B (minutes): ____

## Part C: rubric descriptors (10 minutes)

For each descriptor: is it clear enough that two teachers would agree? Is it age-appropriate for Grades 6–8?

| Item | Clear? (yes/no) | Proposed revision (or "none") |
| --- | --- | --- |
| C1 level 2 | | |
| C1 level 1 | | |
| C1 level 0 | | |
| C2 level 2 | | |
| C2 level 1 | | |
| C2 level 0 | | |
| C3 level 2 | | |
| C3 level 1 | | |
| C3 level 0 | | |
| Value definition `0` | | |
| Value definition `IE` | | |
| "Not scored" line (mechanics) | | |

## Part D: boundaries and open decisions (15 minutes)

Mark each rule **accept**, **revise** or **reject**. A revision must say what changes.

| Rule | Disposition | Revision or reason |
| --- | --- | --- |
| B1 Assessable first | | |
| B2 Length is not the test | | |
| B3 Later criteria follow the response | | |
| B4 Fragments | | |
| B5 Mechanics and transcription | | |
| B6 Embedded instructions | | |
| B7 Off-topic but substantive (proposed `0`) | | |
| B8 Spans | | |
| B9 Rater doubt | | |
| B10 `IE` in analysis | | |
| A1 No abstention → value mapping | | |
| A2 Abstentions cannot be accepted | | |
| A3 A draft does not imply assessable | | |
| A4 Counts for the quality evaluation | | |

Boundary coverage: for each situation, write the response IDs in the set that test it, or "none". This checks
that the set covers each boundary. No key is committed, so your answer is the evidence.

| Situation | Response IDs |
| --- | --- |
| Complete on-task response with every criterion shown | |
| Short, complete response with a claim and no evidence (B2, B3) | |
| Fragment (B4) | |
| Transcription artifacts with recoverable meaning (B5) | |
| Embedded instruction with on-task writing remaining (B6) | |
| Off-topic but substantive (B7) | |
| Claim the passage does not support | |
| Related but imprecise evidence | |

Open decisions. These need an owner's decision, not just a reviewer's opinion. Write the decision and who made it.

| ID | Question | Options | Decision | Decided by |
| --- | --- | --- | --- | --- |
| D1 | Does the P-TER-01 assisted condition show AI-suggested **rubric values**? | (a) Yes, as in PR #30. Then PR #32, which forbids AI values, is not the assisted condition; it stays a separate feedback study. (b) No, feedback text only, as in PR #32. Then PR #30's fixture-adapter drafts must drop their values. | | |
| D2 | At what level does the teacher accept, revise or reject? | (a) Per criterion (PR #30 tables). (b) Per whole draft (PR #32 API). (c) Both, recorded separately. | | |
| D3 | Is an off-topic but substantive response `0` or `IE`? | (a) `0` (B7 as proposed). (b) `IE`. | | |
| D4 | Is `IE` recorded per criterion or for the whole response only? | (a) Per criterion (this candidate). (b) Whole response only. | | |
| D5 | Is attendance an acceptable topic for this pilot? | (a) Yes, as written. (b) Yes, with changes. (c) No, replace it. | | |

## Part E: task and passage (10 minutes)

| Check | yes/no | Note |
| --- | --- | --- |
| The passage is clearly fictional and names no real school, person or district | | |
| Readable for Grades 6–8 | | |
| The prompt can be answered from the passage alone | | |
| More than one valid claim is supported (greeting, breakfast, absence note) | | |
| The passage's limits (late buses, staff time) are clear, so an unsupported claim can be recognized | | |
| Nothing stigmatizes students or families who are absent or late | | |
| No response contains real student information or a real person's name | | |
| The responses look like plausible Grade 6–8 writing for this prompt | | |

## Part F: disposition and sign-off (5 minutes)

Choose one per artifact.

| Artifact | APPROVE / APPROVE WITH REVISIONS / REJECT | Required revisions |
| --- | --- | --- |
| `TASK-ATTEND@0.3` passage and prompt | | |
| `TASK-ATTEND@0.3` responses | | |
| `RUB-ATTEND3@0.3` rubric | | |
| `SCORING_BOUNDARIES.md` | | |

| Field | Entry |
| --- | --- |
| Reviewer ID | |
| Date | |
| sha256 of this completed worksheet (private copy) | |

**APPROVE WITH REVISIONS is not approval.** The revised files get new hashes and need a new Part F.

### After Part F (owner and engineer, not the reviewer)

1. Record the disposition and the worksheet sha256 in `manifest.json` under the matching open item.
2. Only if the rubric is **APPROVE**: the owner sets its final `status`, copies it into
   `backend/app/services/ai_feedback/rubrics/` as `RUB-ATTEND3.v0.3.json`, and computes its pin:

   ```bash
   cd backend && python -c "from app.services.ai_feedback.rubrics import load_registry; \
   print(load_registry()[('RUB-ATTEND3','0.3')].approval_pin())"
   ```

3. The owner adds that pin to `AEOS_AI_FEEDBACK_APPROVED_RUBRICS` in the **deployment environment**, never in
   `.env.example` or in code. The feature flag stays off until every gate in the [README](README.md) is closed.
