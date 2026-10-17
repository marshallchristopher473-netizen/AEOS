# BARS deployment: release evidence and rollback

Part 3 of 3. See also
[BARS_SECURITY_POSTURE_AND_RUNBOOK.md](BARS_SECURITY_POSTURE_AND_RUNBOOK.md)
and [BARS_ADAPTER_CONTRACT_SPEC.md](BARS_ADAPTER_CONTRACT_SPEC.md).

A release decision is only as good as the evidence it is bound to. This
document defines that evidence, the tests that produce it, how a release is
rolled back, and who may approve one.

## Evidence record

Every test result is one record. **A record missing any required field counts
as `NOT TESTED`.** A result from a different SHA, deployment or policy version
does not carry over.

| Field | Required content |
| --- | --- |
| `record_id` | Unique ID |
| `test_id` | ID from the test matrix below, for example `T3` |
| `candidate_sha` | Full 40-character commit SHA. `git cat-file -e <sha>^{commit}` must succeed in the repository being released |
| `deployment_id` | The platform's deployment or version identifier. If the platform exposes none, record that fact and the publish timestamp. Never invent one |
| `environment` | `preview` or `production`, plus the app ID |
| `policy_version` | SHA-256 of the exported entity schemas (including every `rls` block) and backend-function source, as deployed |
| `test_identities` | Synthetic account labels with role and tenant, for example `teacher-a1 / user / tenant-A`. Never real people, and never passwords |
| `expected_result` | Written before the test runs |
| `actual_result` | What happened, including status codes and record counts |
| `outcome` | `PASS`, `FAIL`, `BLOCKED` or `NOT TESTED` only |
| `timestamp_utc` | ISO 8601, UTC |
| `evidence_location` | Path or URL to the raw artifact: request/response transcript, log export or screenshot |
| `executor` | Who ran it |

Example:

```json
{
  "record_id": "EV-0001",
  "test_id": "T1",
  "candidate_sha": "<40-char sha>",
  "deployment_id": "<platform id, or 'none exposed; published 2026-10-20T14:02:00Z'>",
  "environment": "preview / app <app-id>",
  "policy_version": "sha256:<hash of exported schemas + function source>",
  "test_identities": ["teacher-a1 / user / tenant-A", "student-b1 record / tenant-B"],
  "expected_result": "teacher-a1 list read of <Entity> returns 0 tenant-B rows",
  "actual_result": "<observed>",
  "outcome": "NOT TESTED",
  "timestamp_utc": "<iso-8601>",
  "evidence_location": "<path or url>",
  "executor": "<name>"
}
```

## Test matrix

All test data and identities are synthetic. Each test lists its positive
control, so a test that passes because nothing works is caught.

### Containment (posture A)

| ID | Test | Expected |
| --- | --- | --- |
| C1 | Anonymous caller attempts create, read, update and delete on every entity | Denied on every entity and every operation |
| C2 | Ordinary authenticated `user` attempts the same | Denied on every entity and every operation |
| C3 | Positive control: named `admin` performs the same | Allowed |
| C4 | Anonymous caller and ordinary `user` invoke every backend function, including each AI proxy endpoint | `401` and `403` respectively, with no side effect |
| C5 | Ordinary `user` invokes each function that uses the service role | `403`. Proves the function enforces its own authorization (Part 1, F4) |
| C6 | Signed-in non-member loads the app URL | App does not load. Confirms private visibility is applied (Part 1, C2) |

### Self-update (Part 1, C3)

U1–U3 as defined in Part 1. Each attempt is followed by a repeat of a read that
should be denied, to show no new access was gained.

### Tenant isolation (posture B only)

Setup: two tenants, `A` and `B`. Each has at least one ordinary `user` teacher
(not `admin`) and synthetic records. **Every test runs in both directions,
A→B and B→A.** A one-direction pass is a `FAIL`.

| ID | Attack | Expected | Positive control |
| --- | --- | --- | --- |
| T1 | List read of each entity | 0 foreign-tenant rows | Own-tenant rows are returned |
| T2 | Read a foreign record by ID | Indistinguishable from "not found" | Own record by ID succeeds |
| T3 | Update a foreign record by ID | Denied, and the stored value is unchanged on re-read | Own update succeeds |
| T4 | Delete a foreign record by ID | Denied, and the record still exists | Own delete permitted per role |
| T5 | Create a record carrying the foreign tenant's identifier, or referencing a foreign record | Rejected, or stored under the caller's own tenant | Own create succeeds |
| T6 | T1–T5 repeated through every backend function and every enabled adapter operation | Same as T1–T5 | Same as T1–T5 |

**Negative control.** In Preview only, broaden one rule deliberately, confirm
that T1 now reports the breach, then restore the rule and confirm T1 passes
again. This shows the matrix can detect a failure. The approach matches
`docs/P0_MUTATION_VERIFICATION.md`.

### Adapter (Part 2)

Run A1–A6 for every operation proposed for enablement.

| ID | Test | Expected |
| --- | --- | --- |
| A1 | Call a `DISABLED` operation | `OPERATION_DISABLED`. No network call |
| A2 | Send a request that violates the schema | `VALIDATION_FAILED`. No network call |
| A3 | Return an upstream response that violates the schema | `VALIDATION_FAILED`. Nothing is passed to the UI |
| A4 | Force the live call to fail | `UPSTREAM_UNAVAILABLE`. No demo data appears |
| A5 | Send the same mutating request twice | Exactly one write. The repeat returns the original result or is rejected |
| A6 | Update with a stale version | `CONFLICT`. Stored value unchanged |

## Rollback procedure

Reverting the code to an earlier SHA does not restore access rules, functions,
configuration, sessions or data. Base44 access-rule changes take effect
immediately and separately from code (Part 1, F7). Rollback covers all five
layers.

**Before every release, capture a rollback bundle.** Without one, the release
is `BLOCKED`. The bundle contains:

- the previous release's candidate SHA;
- the exported entity schemas, including every `rls` block, and their policy
  version;
- the backend-function source and any version identifiers;
- a configuration snapshot covering visibility, login requirement, the names
  (never values) of secrets, and adapter enablement state.

**To roll back:**

1. **Application code.** Redeploy the previous candidate SHA from the bundle.
   "Baseline" means that recorded SHA, nothing else.
2. **Access rules and functions.** Re-apply the bundle's exported schemas and
   function source. Confirm that the deployed policy version hash matches the
   bundle's.
3. **Configuration.** Restore visibility, the login requirement and adapter
   enablement from the snapshot. Rotate any secret that may have been exposed.
   Restoring the old value is not enough.
4. **Sessions.** If authorization changed, or a credential may have leaked,
   force affected users to sign in again. Whether Base44 can revoke sessions
   is **unverified**. Confirm it during Phase 0. If it cannot, record the
   residual exposure window.
5. **Affected data.** Identify records created or changed during the bad window
   from audit entries or update timestamps. Decide, and record, whether to
   restore, quarantine or keep each one. With synthetic data, this proves the
   procedure works. If real data were ever affected, follow the incident and
   notification obligations, which must be defined before any real-data gate.
6. **Verify.** Re-run C1–C6 against the rolled-back state and record the
   evidence.

**Rollback is complete only when step 6 passes.** Rehearse the full procedure
once in Preview before the first pilot release.

## Sign-off

### P05 is undefined, so it is not a gate yet

The drafts make P05 a sign-off requirement without defining it. Until all four
of the following are written down, P05 is **UNDEFINED** and cannot block or
approve a release:

1. **Scope.** Which tests and records P05 covers.
2. **Reviewer.** A named person who is independent of whoever implemented the
   release.
3. **Reproduction.** What the reviewer re-runs themselves rather than reading.
4. **Vocabulary.** The decisions the reviewer may record.

### Release decision

| Decision | Who may record it | Condition |
| --- | --- | --- |
| `NOT READY` | Anyone | Any required record is missing, `FAIL`, `BLOCKED` or `NOT TESTED` |
| `CANDIDATE READY FOR INDEPENDENT REVIEW` | Implementer, at most | Every required record for the chosen posture is `PASS` on one SHA, deployment and policy version, and a rollback bundle exists |
| `APPROVED FOR SYNTHETIC-DATA PILOT` | Independent reviewer only | The reviewer reproduced the defined evidence on that same SHA, deployment and policy version |

No decision in this table permits real student data. That requires a separate
gate covering consent, a data processing agreement, FERPA and COPPA review,
retention and incident response.
