# P-TER-01 preparation: offline synthetic teacher ELA review

| Field | Value |
| --- | --- |
| Experiment | P-TER-01 offline synthetic teacher ELA review (manual comparator vs. assisted review) |
| This artifact | Preparation harness v0.1. **Preparation only. It is not a run.** |
| Preparation integrity | PASS at the commit that adds this file (see [Verification record](#verification-record)) |
| Run readiness | **BLOCKED.** See [Readiness](#readiness). |
| Data | Authored synthetic Grade 6–8 ELA responses only. No participants, school records, live model or billing. |

## The single missing preparation step

**The authoritative P-TER-01 v0.2 packet was not located.** That packet includes the protocol, the current
Assessment Construct Codebook, and the fixtures and harness the protocol names. Everything that must come from
the protocol is therefore **unbound**: its rubric, measures, thresholds, order procedure and key-visibility rules.

Searched on 2026-10-11, with no copy found:

| Source | Result |
| --- | --- |
| This repository, `main` and all 36 remote branches (file contents and commit messages) | No `P-TER`, codebook or `CIM-0` file |
| GitHub issues and pull requests | No match |
| Notion workspace | No match |
| Google Drive | Mentioned only in *AEOS Claude Ultracode Prompt Pack v0.1* (Prompt 4: "Check whether CIM-0.1 and P-TER-01 are still current"). *AEOS Cabinet Audit 2026-09-30* already records the codebook as **SOURCE NOT LOCATED**. |

This harness does **not** reconstruct the protocol from summaries. It fails closed instead. `manifest.json` records
`protocol` and `codebook` as `SOURCE_NOT_LOCATED`, and `check` reports run readiness as BLOCKED until both are bound
by hash. Once the packet is supplied, run
`freeze --protocol-file <path> --codebook-file <path>`. Then reconcile the rubric, fixtures, measures and order
procedure against it. Re-freezing is required whenever a frozen file changes.

## What was preserved

No existing file was modified. The existing teacher-review evidence harnesses are
`docs/evidence/teacher-review-offline-check.py` and `backend/tests/review_fixture_server.py`. They exist only on the
unmerged `feat/teacher-assessment-review` and release-candidate branches, not on `main`, and they were not touched.
This preparation is file-based and independent of the AEOS backend. Whether the assisted condition must run through
the AEOS review UI is a protocol question; it is still open.

## Contents

| Path | Role | Status |
| --- | --- | --- |
| `fixtures/passage.PSG-COOLROOF.v0.1.json` | Original informational passage and prompt (Grade 6–8) | PROPOSED-UNREVIEWED |
| `fixtures/rubric.RUB-CER3.v0.1.json` | Provisional 3-criterion claim/evidence/reasoning rubric (`0`, `1`, `2`, `IE`) | PROPOSED-UNREVIEWED. It does not replace the codebook rubric. |
| `fixtures/responses.v0.1.json` | 10 authored synthetic responses in two matched sets (S1, S2) | PROPOSED-UNREVIEWED |
| `fixtures/drafts.fixture-adapter.v0.1.json` | Assisted-condition drafts from a frozen deterministic adapter: value, evidence span, rationale | PROPOSED-UNREVIEWED |
| `harness/pter01.py` | Freeze, schedule, packet, blank-tables and check commands. Standard library only. | v0.1 |
| `harness/test_pter01.py` | 27 behavioral and mutation tests | v0.1 |
| `manifest.json` | sha256 of every frozen file, version links, key hash, unbound thresholds, open items | Frozen |
| *(not committed)* provisional key | Provisional per-criterion key values and spans, response profiles, seeded draft errors | PROVISIONAL-UNREVIEWED, **hidden** |

Each response set contains five profiles: strong, ambiguous, insufficient evidence, an access-support variation
(dictated speech-to-text) and an instruction-injection attempt. The response-to-profile mapping and the
draft-versus-key differences live only in the hidden key. The fixtures were authored by an AI assistant for this
preparation. They are not student work and are not representative of any class. The passage's library example
is fictional.

### Hidden key

This repository is **public**, so the provisional key is never committed. `manifest.json` stores only its sha256
(`725f599b…`). The key file also contains a random nonce, so its contents cannot be guessed from the hash. The key
was delivered outside the repository, and its owner must store it in the private evidence store. `freeze` refuses
a key path inside the repository. `check --key` verifies the hash, coverage, values, evidence spans and the
seeded-error flags. `.gitignore` excludes `keys/`, `*key*.json` and `runs/`.

## Design

### Conditions stay separate

| | Manual comparator | Assisted review |
| --- | --- | --- |
| Packet | Passage, prompt, rubric, responses | Same, plus one frozen draft per criterion and a notice that drafts may be wrong |
| Criterion table columns | `final_value`, `final_span_*`, `rater_span_supports`, `note` | Adds `draft_id`, `original_value`, `original_span_*` (prefilled from the frozen draft) and `decision` |
| `adapter_ref` | `not_applicable` | `fixture-adapter@0.1` |
| Output directory | `<run>/outcomes/manual/` | `<run>/outcomes/assisted/` |

Each condition has its own `sessions.csv`, `tasks.csv` and `criteria.csv`. `check` rejects a table whose columns
do not match its condition's template. It also rejects a manual packet that contains drafts.

### Frozen versions

Passage `PSG-COOLROOF@0.1`, rubric `RUB-CER3@0.1`, response set `0.1`, adapter `fixture-adapter@0.1`, and
harness `0.1` are all bound by sha256 in `manifest.json`. The protocol and codebook are recorded as
`SOURCE_NOT_LOCATED`. Every schedule and outcome row carries `manifest_sha256`. Task rows also carry the
passage, rubric, response-set and adapter versions.

### Measures captured

| Required capture | Where |
| --- | --- |
| Explicit teacher accept / revise / reject | `assisted/criteria.csv` → `decision` |
| Original and final values | `original_value`, `original_span_*` (assisted); `final_value`, `final_span_start/end/quote` (both) |
| Evidence-span validity | Mechanical validity (offsets inside the response and the quote matches the text) is checked by `check`. Whether the span actually supports the score is an independent rater judgment, recorded in `rater_span_supports` (`yes`/`no`/`partial`). |
| Setup time | `sessions.csv` → `setup_time_s` (per tester per condition) |
| Active review time | `tasks.csv` → `active_review_s` |
| Pause / repair time | `tasks.csv` → `pause_repair_s` |
| Abandonment | `tasks.csv` → `task_status=abandoned`, `abandoned_stage`; `sessions.csv` → `session_status` |
| Failures | `tasks.csv` → `task_status=failed`, `failure_code`, `failure_note` |

### Denominators and missing data

- The denominator is the **scheduled task**. Blank tables contain one row per scheduled task and criterion. A
  deleted, duplicate or unscheduled row is an integrity failure.
- **A blank cell is a missing outcome.** Nothing is imputed, defaulted or coerced to zero. `not_applicable` marks
  fields that do not apply by design, such as the adapter in the manual condition.
- `check` reports counts only, as `k/n` against the scheduled denominator, with `missing` shown explicitly. It
  computes no rates, averages, savings or pass/fail against thresholds.
- Decision consistency is enforced. An `accept` row must equal the draft; blank span cells on `accept` or `revise`
  mean the draft's span stands. A `revise` row must differ from the draft. A `not_started` task cannot carry
  outcomes.

### Order procedure (PROPOSED)

The protocol's order and randomization requirement is unknown. `schedule` provides a seeded procedure that can be
adopted or replaced:

1. Shuffle the testers with the recorded seed, then cycle them through four arms: condition order
   (manual→assisted or assisted→manual) × set assignment (S1 or S2 to the manual condition). It is balanced when
   the tester count is a multiple of 4.
2. Each tester sees each response set exactly once, so no response is reviewed twice.
3. The response order within each block is shuffled with the same seed.
4. The schedule records the seed and the manifest hash. The same inputs reproduce the same schedule.

### Thresholds

None are bound. When the protocol is located, copy its measures and thresholds into `manifest.json`
`thresholds.values` with status `BOUND-AS-PROPOSALS`. They remain **proposals, not validated cutoffs**. The harness
never applies them.

## Replay commands

Run from the repository root. Keep `runs/`, packets, schedules and filled tables in private storage, not in Git.

```bash
H=docs/pilots/teacher-synthetic/harness/pter01.py
KEY=/private/path/P-TER-01-provisional-key.v0.1.json   # outside the repository
RUN=/private/path/runs/RUN-ID

python3 $H check --key "$KEY"                               # fixtures, versions, spans, key
python3 $H schedule --run-id RUN-ID --testers T01,T02,T03,T04 --seed <recorded-seed> --out "$RUN/schedule.json"
python3 $H packet --schedule "$RUN/schedule.json" --tester T01 --condition manual   --out "$RUN/packets"
python3 $H packet --schedule "$RUN/schedule.json" --tester T01 --condition assisted --out "$RUN/packets"
python3 $H blank-tables --schedule "$RUN/schedule.json" --out "$RUN/outcomes"
python3 $H check --key "$KEY" --schedule "$RUN/schedule.json" --packets "$RUN/packets" --outcomes "$RUN/outcomes"
python3 $H check --key "$KEY" --require-run-ready           # exit 2 while any run gate is open

python3 -m unittest discover -s docs/pilots/teacher-synthetic/harness -v
```

Tester IDs are pseudonymous placeholders. `check` exits `0` when integrity passes, `1` on any integrity failure,
and `2` with `--require-run-ready` while run gates are open.

### What `check` verifies

1. Every frozen file matches its manifest sha256. The passage, rubric, response set, drafts, adapter and manifest
   versions all link to each other.
2. Every draft evidence span lies within its response and quotes it exactly. Scores of `1` or `2` require a span;
   scores of `0` and `IE` must not have one. Drafts cover every response × criterion exactly once.
3. With `--key`: the key's hash, location (outside the repository), coverage, values and spans, and that the
   seeded-error flags match the actual draft-versus-key differences.
4. With `--schedule`: the schedule was built from the current manifest; each tester has one block per condition
   and sees each set once.
5. With `--packets`: no key-only field or key nonce appears in any packet; manual packets contain no drafts.
6. With `--outcomes`: the table templates per condition, the denominator against the schedule, the version
   columns, enumerations, non-negative times, teacher evidence spans, consistency between originals and drafts,
   and decision consistency.

## Readiness

### Readiness for preparation: READY

The fixtures, adapter, harness and manifest are frozen, and the local integrity checks pass. The blank tables,
packets and order procedure can all be generated and replayed.

### Readiness to run: BLOCKED

| Gate | Status | Resolves when |
| --- | --- | --- |
| P-TER-01 v0.2 protocol source | OPEN (SOURCE_NOT_LOCATED) | The packet is located, bound by hash, and fixtures, measures and rubric are reconciled to it |
| Assessment Construct Codebook | OPEN (SOURCE_NOT_LOCATED) | Located and bound by hash |
| Independent fixture review | OPEN | A qualified Grade 6–8 ELA reviewer records a disposition for the passage, rubric and responses |
| Independent key review | OPEN | An independent reviewer adjudicates the provisional key, including ambiguous items and seeded errors |
| Independent comparator review | OPEN | A reviewer confirms that the manual condition is a fair equivalent task |
| Order procedure | OPEN | The protocol's requirement is confirmed and the proposed schedule is adopted or replaced |
| Thresholds | OPEN (UNBOUND) | The protocol's values are copied as proposals |
| Adult tester notice | OPEN | The notice is prepared, approved and delivered per protocol |

An item closes only when `manifest.json` records `RESOLVED` with an evidence reference. No item has been resolved.

## Not done, by instruction

No one was recruited. No notice was sent. No tester response, consent, timing or time saving was created. No
independent approval was recorded. No live model, billing, network, database or school record was used. No score
was released. The provisional key was not shared with testers.

## Permitted claims

The fixtures and harness can be replayed and integrity-checked offline. Nothing here shows teacher time savings,
review quality, scoring accuracy, assessment validity, fairness or student learning.

## Known risks

- **Public repository:** a tester who browses the repository can read the fixtures and drafts before a session.
  The protocol should state whether testers may have repository access.
- **Provisional content:** the rubric and responses may diverge from the codebook. Reconciliation can change the
  fixtures, which requires re-freezing and invalidates earlier schedules.
- **Small fixture set:** one passage and five profiles per set. The responses are AI-authored, so they are not
  representative of real student writing.
- **Key custody:** if the private key copy is lost, the hash can no longer be satisfied, and a new key must be
  authored and independently reviewed.

## Verification record

Recorded on 2026-10-11 with Python 3.13.16 on Linux, in an offline container.

| Check | Result |
| --- | --- |
| `check --key <private key>` | Preparation integrity PASS (0 failures); run readiness BLOCKED with 11 open blockers |
| Dry run: 4 placeholder testers, seed 20261011, 8 packets, blank tables, full `check` | PASS. 20 scheduled tasks per condition, 60 criterion rows per condition, all outcomes `missing` |
| `check --require-run-ready` | Exit 2 (BLOCKED), as intended |
| `python3 -m unittest discover -s docs/pilots/teacher-synthetic/harness -v` | 27 passed |
| Key-content scan of committed files | No key nonce or key-only field present |
