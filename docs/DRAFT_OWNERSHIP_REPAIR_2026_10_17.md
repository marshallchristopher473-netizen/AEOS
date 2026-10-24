# AI feedback draft-ownership repair

This repair sits on the PR #42 pilot candidate,
`bc450865899f1b2eeba5c5558b16254624ba6f43`. It closes one authorization gap in
the teacher feedback workflow. It does not approve P0, the pilot, a merge, or a
deployment.

## Defect

On the candidate, a feedback draft was scoped to the organization only:

| Same organization, Teacher B acting on Teacher A's draft | Before | After |
| --- | --- | --- |
| `GET /ai-feedback/drafts/{id}` (includes the student response) | 200 | 404, same as a missing draft |
| `GET /ai-feedback/drafts?assessment_id=…` | lists A's drafts | lists only B's own |
| `POST /ai-feedback/drafts/{id}/decisions` (accept / revise / reject) | 201, becomes the current decision | 404 |
| Direct Supabase read of A's request, draft, decision (`authenticated` role) | visible | not visible |
| Decision row with `decided_by` ≠ requester (even from the service role) | accepted | refused by trigger |

Support staff had the same read access as a peer teacher. An org admin could
also record the decision on any teacher's draft.

## Rule after the repair

| Actor (same organization) | Read draft | Decide draft |
| --- | --- | --- |
| Teacher who requested it | yes | yes |
| Org admin | yes (oversight) | no: 403 `not_draft_owner` |
| Other teacher, support | no: 404 | no: 404 |

The API service and the database enforce the same rule. Neither one depends on
the other.

## Changes

| File | Change |
| --- | --- |
| `backend/app/services/ai_feedback/service.py` | Ownership check on get, list and decide |
| `backend/supabase/migrations/007_ai_feedback_draft_ownership.sql` | New, forward-only. Requester-or-admin SELECT policies on the three tables; the decision integrity trigger also requires `decided_by` = the request's `created_by` |
| `backend/tests/test_ai_feedback.py` | 5 new API tests; the support-role assertion changed from 200 to 404 |
| `backend/tests/test_ai_feedback_rls.py` | Ownership read matrix, positive control, negative control and a decider test against PostgreSQL. The read test replaces the old org-wide one. Two positive cases that had a peer or an admin deciding Teacher A's draft now use the requester. |
| `backend/tests/security_mutations.py`, `test_rls_enforcement.py` | Apply 007. Mutations M21a–g |
| `docs/AI_FEEDBACK_DRAFTING.md`, `docs/P0_MUTATION_VERIFICATION.md` | Updated to the new rule |

No frontend change. The panel already shows the server's `{code, message}`
error text.

## Executed locally

Python 3.11.17 venv (CI pins 3.11.15), PostgreSQL 16.15 on localhost, synthetic data only.

| Check | Result |
| --- | --- |
| Full backend suite on the unmodified candidate, `AEOS_REQUIRE_RLS_TESTS=1` | 538 passed, 0 skipped |
| New and changed API tests on the **unfixed** service | 5 failed (peer read 200, peer decide 201, peer key replay 201, list leak, admin decide 201), 1 passed (admin deciding their own draft, a positive control) |
| New and changed DB tests on migrations 001–006 (**unfixed**) | 7 failed (peer/support read on all 3 tables, ownership positive control on all 3, trigger accepted peer and admin deciders); negative control passed |
| Full backend suite after the repair, `AEOS_REQUIRE_RLS_TESTS=1` | **548 passed, 0 skipped** |
| Backend suite without a database (CI `backend-tests` mode) | 293 passed, 255 skipped |
| M21 mutations (a–g) | 7 killed, 0 survived, 0 invalid |
| Full mutation contract | see the PR description for this run's result |

## Not verified

- Hosted Supabase: 007 has not been applied to any hosted project. The
  `postgres` role that owns the SECURITY DEFINER helpers must bypass RLS there,
  which is the same assumption migrations 002–006 already make.
- Real teacher sign-in. Only dependency-overridden actors and `SET ROLE
  authenticated` sessions were exercised.
- Whether admins should read every teacher's drafts is a product decision.
  This repair keeps admin read access for oversight. Removing it is a one-line
  change in each layer.
