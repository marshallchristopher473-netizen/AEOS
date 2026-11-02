# Static demo claims-integrity repair

Status: builder checks pass; independent browser re-verification pending. Do not publish on this record alone.

## November 2 independent-review follow-up

Independent review rejected the first repair head 40a7ef59967bd737de818d8d59cd5deeae1634f3:
its blank/OFF_TOPIC responses could acquire numeric scores through REVISE even
though their mock scores were null. The follow-up blocks numeric actions and
final scored decisions for blank, whitespace-only and OFF_TOPIC responses;
the UI disables the corresponding revision controls. Criterion flagging and
REJECT remain available after inspection, with null final scores.

Four additional regression/renderer checks cover both affected fixtures,
whitespace without a mock flag, final-decision defense against stale numeric
criterion state, and disabled UI controls. Current builder result: all five
syntax checks and 34 Node tests pass, zero failed/skipped. The original 30-test
result below is historical and did not establish this boundary. The new exact
candidate must receive fresh independent verification before publication.

A second independent check at 1756d35d0a96b2bcec34828bc3f54f0edb7aca9c found
that the partially insufficient R-005 still allowed its unscored Conventions
criterion to receive a numeric revision. The bounded demo now preserves every
fixture null/undefined score: both numeric action guards and final-decision
guards block scoring, including stale criterion state, and the UI disables
that criterion's numeric controls. Flagging and reasoned rejection remain.
Three further tests exercise the null criterion, stale finalization and its UI.
These are demo constraints, not an approved live abstention/override policy.
Latest builder validation: all five syntax checks and 37 Node tests pass,
zero failed/skipped. Fresh independent acceptance is still required.

Source: PR #54 at 6ec4db7595b9334e408c32b20f09f66c8ca9811f.
Replacement base: main at b9c68aa3e6fe35f676da04c10683bfdda12a9eed.

## Findings addressed

- F1: removed the manual-baseline form, baseline storage, assisted/manual comparison and difference calculation. The remaining timing field is demoClickThroughMedianSec. Both dashboard and export identify prewritten/mock interaction time. Export schema v2 includes DEMO_CLICKTHROUGH_NOT_GRADING_TIME and retains DEMO_SYNTHETIC_NOT_EVIDENCE.
- F2: button.link and .decision-option have a 28px minimum height; labels use inline-flex. Actual 390px rendered dimensions remain an independent browser check.
- F3: this candidate carries only demo/pilot-review/** and .github/workflows/pilot-demo.yml. It excludes #54's dependency port, frontend files and P0 workflow edit. It does not rewrite the old branch.
- F4: CSV serializer escapes comma, quotes, CR and LF; the export allowlist remains aggregate-only.

No changes to fixture content, CSP, network capabilities, auth, persistence, migrations, RLS or feature flags. This does not approve AEOS P0 or P-TER-01.

## Builder verification

Node v24.22.1; syntax checks pass for all five scripts, including both test files. Node tests: 30 passed, 0 failed, 0 skipped. Existing evidence/decision/blank/injection/audit/export tests remain; new coverage exercises the original 600-second/4.1-second case, rejects legacy timing fields in v2, retains unmeasured null values, checks CSV escaping and executes app.js with a minimal test DOM.

The renderer contract uses a test DOM. It is not a browser, layout, screen-reader or mobile-device test.

The browser available in this session could not connect to the local test server (ERR_CONNECTION_REFUSED). No attempt was made to route around that boundary. Earlier /tmp harness paths from another environment were not available here. No independent browser pass is claimed.

## Independent re-verification

Use the replacement PR's exact full head SHA and a fresh clean worktree. Re-run syntax and Node tests. Re-run the saved browser harness if accessible, updating its timing assertions to require:
1. No manual-baseline input, comparison or numeric time-difference field.
2. Dashboard timing described as active demo interaction over prewritten mock suggestions, not grading time or time saved.
3. JSON/CSV schema v2 with demoClickThroughMedianSec, DEMO_CLICKTHROUGH_NOT_GRADING_TIME and DEMO_SYNTHETIC_NOT_EVIDENCE; no legacy baseline/difference/assisted time values.
4. Link buttons and decision labels measured at least 24px high at a 390px viewport.
5. All prior evidence, accept/revise/reject, reason, reset/reload, privacy, CSP/network and aggregate-only export behavior preserved.

Run a complete source diff against main and confirm only the demo directory and its own workflow changed. Record CI results separately from builder tests. The inherited frontend/dependency gate on old main must not be fixed by expanding this demo candidate.

Return DEMO READY FOR DEPLOYMENT, DEMO REJECTED or DEMO BLOCKED for that exact SHA. A builder pass alone does not change the original independent rejection.

