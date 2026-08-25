---
applyTo: "backend/app/**"
---

# Backend security instructions

## Current, verified state (do not assume this has changed without checking)

- `backend/app/core/auth.py` verifies JWT signature (JWKS/RS256), expiration, audience (`"authenticated"`), and issuer.
- `backend/app/core/dependencies.py` has `get_current_actor`, which resolves the JWT `sub` claim to an AEOS `users` row (matched on `auth_user_id`) and returns a trusted `AuthenticatedActor(user_id, organization_id, role, auth_user_id)`.
- As of the last verification, `get_current_actor` is **not yet wired into any business route**. `backend/app/api/students.py`, `assessments.py`, and `intervention_plans.py` still: (a) declare no auth dependency at all, (b) accept `organization_id`/`created_by` as client-supplied request fields, (c) filter reads only by resource ID with no tenant scoping, and (d) use `get_supabase_admin_client()` (the service-role key, which bypasses RLS) for ordinary CRUD.

Re-verify this against the actual files before relying on it — this note can go stale.

## Non-negotiable rules for any route you touch or add

1. **Every business route must depend on `get_current_actor`** (or a narrower dependency built on top of it). No route that reads or writes tenant-owned data may be reachable without it.
2. **Never accept `organization_id`, `created_by`, `user_id`, `owner_id`, or `role` as client-writable request fields.** Derive them from the `AuthenticatedActor` returned by `get_current_actor`. If a request model currently has one of these fields, removing it and deriving the value server-side is the fix — not validating the client's value.
3. **Every read and write must be scoped by the actor's `organization_id`.** `SELECT ... WHERE id = :id` is not sufficient — it must be `WHERE id = :id AND organization_id = :actor_org_id`, and a mismatch should return 404 (don't leak existence of another tenant's row).
4. **Validate cross-entity relationships stay within the same tenant.** E.g. before creating an assessment for a student, confirm that student's `organization_id` matches the actor's, not just that the student exists.
5. **Prefer a non-service-role Supabase client for ordinary request handling.** The admin/service-role client bypasses RLS entirely and should be reserved for genuine administrative/background operations — using it for routine CRUD defeats RLS as defense-in-depth even after RLS policies exist.
6. **Every new route or auth behavior needs a same-tenant test AND a cross-tenant/negative test** in `backend/tests/`. A route with only happy-path tests against a fully-mocked client that never checks for an auth header is not tested for security — see the pre-existing tests in `test_students.py`/`test_assessments.py`/`test_intervention_plans.py` for what NOT to imitate; they don't send tokens and don't assert 401/403.
7. **Do not mock the function under test.** Mock only external boundaries (JWKS/HTTP calls, the Supabase client). Call the real dependency function directly, as `backend/tests/test_dependencies.py` does.

## Failure-mode mapping (keep consistent)

- No/garbage/expired/wrong-audience/wrong-issuer token → 401
- Valid token, but no matching AEOS `users` row → 401
- Valid token, matching row, but `status != "active"` → 403
- Valid actor, but the requested resource belongs to a different `organization_id` → 404 (not 403 — don't confirm the resource exists in another tenant)
