# BARS Prompt 3: hosted evidence harness

This bash harness checks the BARS ownership and persistence requirements
(Prompt 3, R2–R21) against a **hosted** BARS deployment. For each check it
records the expected and actual result, then builds a manifest you can attach
to the handoff.

It tests a deployment. It does not stand in for one. The BARS server source is
**not in this repository**, so `deployed_git_sha` cannot yet be tied to a
commit here.

## Files

| File | Role |
| --- | --- |
| `env.sh` | Checks preconditions, then exits 2 before writing anything if one is unmet |
| `lib.sh` | `http`, `record`, `record_blocked`, `record_notrun` |
| `run.sh` | Ordered checks C01–C30 |
| `restart-check.sh` | C30. Run it after you restart the deployment |
| `report.sh` | Turns `checks/C??.json` into `manifest.json` and `report.md` |
| `environment.txt.example` | Template for the operator's R1 attestation |
| `checks/` | Per-run records and raw bodies. Gitignored |

## Preconditions (run.sh refuses to start without them)

1. `BASE` is an `https://` hosted URL. Localhost, `127.*`, `0.0.0.0`, IPv6
   literals and `*.local` are refused.
2. Two distinct approved synthetic testers: `TESTER_A_EMAIL` / `TESTER_A_PIN`
   and `TESTER_B_EMAIL` / `TESTER_B_PIN`.
3. `evidence/bars/environment.txt`, copied from the example, with every
   `<placeholder>` replaced and `database_is_shared_with_dev: no`.
4. `curl` and `jq` are installed.
5. Nobody has been invited yet. This runs before Prompt 5.

## Run

```bash
export BASE='https://<your-replit-domain>'
export TESTER_A_EMAIL='tester1@example.test' TESTER_A_PIN='<pinA>'
export TESTER_B_EMAIL='tester2@example.test' TESTER_B_PIN='<pinB>'

bash evidence/bars/run.sh;  echo "exit=$?"
bash evidence/bars/report.sh
# Restart the Replit deployment, then:
bash evidence/bars/restart-check.sh
bash evidence/bars/report.sh      # folds C30 in
```

| run.sh exit | Meaning |
| --- | --- |
| 0 | No FAIL. BLOCKED and NOT RUN items may still be open |
| 1 | One or more FAIL |
| 2 | A precondition is unmet. Nothing was written |
| 3 | Fixture setup failed (sign-in, create or edit). The run is incomplete |
| 4 | A tester email or PIN appeared in `checks/`. Do not share that run |

`report.sh` gives one verdict: `FAIL`, `BLOCKED`, `AUTOMATED PASS — n manual
item(s) still open`, `PASS`, or `INVALID`. `INVALID` means records came from
another run, or the run never finished.

## What each check needs to pass

- **C06–C11** (cross-tester read, edit, delete, focus, reflection) expect 404.
  C15 is their positive control: A must still read the task with its title
  unchanged.
- **C12** passes only if B's list is a real JSON array without A's task *and*
  A's own list contains it. An endpoint that always returns `[]` fails.
- **C14** passes only if B's task, created with A's id in the body, is
  readable by B and returns 404 to A.
- **C20** sends five parallel POSTs with an **identical body and identical
  `Idempotency-Key`**, as a double-click would. Exactly one record may result.
- **C24** passes only if A reads back `focusMinutes: 40` and B does not see
  it.
- **C30** uses a dedicated restart fixture, which C21 does not delete, and
  checks that its title survived.

## Stop rule

If `run.sh` exits non-zero, do not retry with different inputs. Hand over the
failing check ID, its `checks/<id>.body.json`, `environment.txt`, and the
smallest repair. Do not run Prompt 5 or invite anyone while there is a FAIL,
a BLOCKED item or an INVALID result.

## What this does not prove

- That the deployment is invite-only. That is Prompt 5.
- What a browser does: localStorage (C27), input kept on error (C28), safe
  retry (C29). These need DevTools or UI fault injection.
- That there is one database per environment. That rests on the operator's
  attestation in `environment.txt`.
