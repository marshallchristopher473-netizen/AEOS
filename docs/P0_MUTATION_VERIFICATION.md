# P0 security mutation verification

This document records how the AEOS P0 multi-tenant security boundary is
verified, what the verification covers, and what it deliberately does not
cover. It is a method record, not a claim of certification. A separate
reviewer must reproduce it independently before P0 can be closed.

## Why mutation testing is the gate

A green security suite proves nothing on its own. The specific failure this
repository guards against is a regression that leaves a policy's *name* intact
while removing its effect — `students_select` becoming `USING (true)`.
`test_security_artifacts.py` asserts `"CREATE POLICY students_select" in sql`,
which such a regression satisfies exactly. Only executing a broken copy and
watching the suite fail distinguishes a suite that tests something from one
that does not.

## What counts as a killed mutation

A mutation is **KILLED** only when the mutated tree still builds and a *test
assertion* fails. The following are explicitly **not** kills, and are reported
as `INVALID MUTATION` instead:

- syntax errors and byte-compilation failures
- import errors and collection errors
- missing dependencies
- database connection failures
- migration failures
- mutation-harness errors (including stale anchors)

Every mutant therefore passes a validity precheck before any test runs:

| Target | Precheck |
| --- | --- |
| Python (`*.py`) | `compileall` the tree, then import `app.main` |
| SQL migration (`*.sql`) | apply shim + migrations 001–005 to a scratch database; every statement must succeed |
| Frontend (`*.ts`) | textual substitution only; no build step in this harness |

Each mutant is then run against the smallest relevant security subset **and**
against the complete suite, so an interaction failure cannot hide.

## Running the verification

```bash
# 1. Disposable PostgreSQL 16, never a production database
export AEOS_TEST_DATABASE_URL=postgresql://postgres@localhost:5432/postgres

cd backend
pip install -r requirements-dev.txt

# 2. Unmodified baseline — must be green before anything else means anything
python -m pytest tests/ -q

# 3. Complete M01-M20 mutation contract
python -m tests.security_mutations --json mutation-matrix.json

```

Both run in CI (`.github/workflows/p0-backend-tests.yml`) against a
PostgreSQL 16 service container, and the matrix is uploaded as a build
artifact keyed to the exact commit SHA.

`AEOS_REQUIRE_RLS_TESTS=1` turns a missing database into a hard failure rather
than a silent skip, because a security test that skips quietly is worse than no
test: CI stays green while proving nothing.

## The M01–M20 contract

| ID | Security boundary | Mutation | Primary killing test |
| --- | --- | --- | --- |
| M01 | Every route requires a verified bearer token | authentication dependency replaced by a constant subject | `test_route_authentication.py::test_every_business_route_requires_authentication` |
| M02 | Claims are trusted only after full verification | `jwt.decode(...)` → `jwt.get_unverified_claims(token)` | `test_auth.py::test_forged_signature_is_401` |
| M03 | Actor identity is the DB row selected by verified `sub` | client `user_id` claim overrides the resolved actor | `test_dependencies.py::test_client_supplied_user_id_claim_cannot_replace_the_resolved_actor` |
| M04 | Tenant authority is derived server-side | client `organization_id` claim overrides tenant | `test_dependencies.py::test_client_supplied_organization_id_claim_cannot_grant_another_tenant` |
| M05 | Cross-tenant student SELECT denied | `students_select` → `USING (true)` | `test_rls_enforcement.py::TestCrossTenantSelectDenial::test_foreign_tenant_row_is_invisible[students]` |
| M06 | Cross-tenant assessment SELECT denied | `assessments_select` → `USING (true)` | `TestCrossTenantSelectDenial::test_unfiltered_scan_returns_only_own_tenant[assessments]` |
| M07 | Cross-tenant plan SELECT denied | `intervention_plans_select` → `USING (true)` | `TestCrossTenantSelectDenial::test_foreign_tenant_row_is_invisible[intervention_plans]` |
| M08 | Cross-tenant result SELECT denied | `assessment_results_select` → `USING (true)` | `TestCrossTenantSelectDenial::test_foreign_tenant_row_is_invisible[assessment_results]` |
| M09 | Organization suspension removes access | `tenant.status = 'active'` dropped from `aeos_has_org_access`, `aeos_can_write_org`, `aeos_is_org_admin`; and from application actor resolution | `TestOrganizationLifecycle::test_suspended_organization_cannot_read`; `test_dependencies.py::test_suspended_organization_is_forbidden` |
| M10 | Membership/user deactivation removes access | `membership.status = 'active'` dropped from `aeos_has_org_access`; `status=active` dropped from user lookup | `TestOrganizationLifecycle::test_disabled_member_cannot_read` |
| M11 | DELETE reserved to organization admins | `students_delete` widened admin → teacher | `TestPeerAccessSemantics::test_teacher_may_not_delete_peers_student` |
| M12 | INSERT binds `created_by` to the acting user | `students_insert` drops the actor binding | `TestCrossTenantInsertDenial::test_insert_claiming_foreign_creator_is_rejected` |
| M13 | FK relationships stay inside the tenant | `assessments_insert` FK check collapsed to a tautology | `TestCrossTenantInsertDenial::test_assessment_cannot_reference_foreign_tenant_student` |
| M14 | `organization_id` / `created_by` immutable on UPDATE | identity trigger neutered | `TestPeerAccessSemantics::test_ownership_columns_remain_immutable_on_peer_update` |
| M15 | Service-role queries carry a server-derived tenant | list and get-by-id drop their tenant filter | `test_students.py::test_cross_tenant_student_object_is_indistinguishable_from_missing` |
| M16 | Service-role credential never reaches an ordinary request | browser falls back to `SUPABASE_SERVICE_ROLE_KEY` when no user token is present | `test_security_artifacts.py::test_service_role_key_is_not_referenced_by_frontend_source` |
| M17 | Authentication and authorization deny by default | missing credentials return a default subject; role check always allows | `test_auth.py::test_missing_credentials_are_401`; `test_authorization.py::test_support_role_is_forbidden_from_privileged_writes` |
| M18a | Expired tokens rejected | `verify_exp: False` | `test_auth.py::test_invalid_required_claims_are_401[exp]` |
| M18b | Wrong issuer rejected | `verify_iss: False` | `test_auth.py::test_invalid_required_claims_are_401[iss]` |
| M18c | Wrong audience rejected | `verify_aud: False` | `test_auth.py::test_invalid_required_claims_are_401[aud]` |
| M18d | Invalid signature rejected | `verify_signature: False` | `test_auth.py::test_forged_signature_is_401` |
| M18e | Missing `kid` rejected | fall back to the first published key | `test_auth.py::test_token_without_a_key_id_is_401` |
| M18f | Unknown `kid` rejected | fall back to the first published key | `test_auth.py::test_unknown_key_id_is_401_even_though_a_usable_key_is_published` |
| M18g | Malformed tokens fail closed | JWT error path returns a default subject | `test_auth.py::test_malformed_token_is_401` |
| M18h | Unusable published keys fail closed as 401 | `JWKError` re-raised past the 401 handler (the pre-SEC-G1-06 behaviour) | `test_auth.py::test_unusable_published_key_is_401_not_a_server_error[*]` |
| M19a | Client roles hold no privilege RLS does not govern | 005 stops revoking TRUNCATE on existing tables | `TestPrivilegesRlsDoesNotGovern::test_client_roles_hold_no_rls_blind_privilege`; `test_cross_tenant_truncate_is_refused[*]` |
| M19b | Tables created later do not regain TRUNCATE | 005 stops revoking TRUNCATE from the default privileges | `TestPrivilegesRlsDoesNotGovern::test_tables_created_later_do_not_inherit_rls_blind_privileges` |
| M20 | WHERE-less writes cannot reach another tenant on any table | `ai_recommendations_delete` → `USING (true)` | `TestWherelessWritesAcrossEveryTable::test_whereless_delete_leaves_org_a_untouched[*-ai_recommendations]` |

### On M18e and M18f

The weakening these guard against is not "no key found" — that already fails
closed — but "guess the key anyway". Both mutants therefore fall back to the
first published JWKS key, and both new tests sign with the **real** key so that
a guessing implementation would genuinely accept the token.
`test_unknown_signing_key_is_401` alone could not detect this: it publishes a
JWKS with no usable key, so a guessing implementation still fails.

## No mutant is excluded from the score

Every mutant in the contract is scored. There is no EQUIVALENT category in use
and no mutant is excluded from the denominator.

This is a correction. An earlier revision excluded exactly one mutant —
removing `AND tenant.status = 'active'` from `aeos_can_write_org` — as proved
equivalent, and shipped a 29/29 score on that basis. **Independent verification
refuted the proof.** The mutant is live and non-equivalent.

The proof's reasoning was that "UPDATE and DELETE must first locate the row,
which applies the SELECT policy governed by `aeos_has_org_access`". That holds
only for statements carrying a `WHERE` or `RETURNING` clause. PostgreSQL applies
a table's SELECT policy to an UPDATE only when the statement must locate rows,
so a bare `UPDATE students SET ...` never consults it and `students_update`'s
`USING` clause — `aeos_can_write_org` alone — is the only remaining control.
`students_update`'s `WITH CHECK` adds nothing for a row with `school_id IS NULL`,
because that conjunct is then satisfied vacuously.

All 20 probes in the withdrawn proof used `WHERE`, so all 20 were masked by the
SELECT policy and the mutation looked inert. Against a suspended tenant the
mutant in fact returns `UPDATE 1` and persists the unauthorized value.

`tests/equivalence_proof_can_write_org.py` has been deleted along with its CI
step: its premise is refuted and there is no equivalence claim left to re-prove.

The mutant is now killed behaviourally by
`tests/test_rls_enforcement.py::TestOrganizationLifecycle::test_suspended_organization_cannot_update_without_a_where_clause`,
which issues an UPDATE with no `WHERE` and no `RETURNING` against a student row
with `school_id IS NULL` in a suspended organization, and asserts both that the
statement affects zero rows and that the stored value is unchanged.

## Negative controls

Two independent mechanisms show the suite can observe a breach rather than
merely passing:

- `test_rls_enforcement.py::TestNegativeControl` disables the specific RLS
  protection under test and asserts the same attack then succeeds — covering
  SELECT, unfiltered scan, UPDATE, DELETE, INSERT and suspension denial, and
  it re-grants TRUNCATE to show the cross-tenant wipe that 005 prevents, and
  switches RLS off per table to show the WHERE-less sweep sees every write. If
  those ever stop observing a breach, the module has become vacuous.
- The mutation contract above, which breaks each control at source and records
  the assertion that fires.

## Scope and limits

- **Synthetic data only.** Every row is generated in the test files. No real
  student information is used at any point.
- **Disposable databases only.** Each run creates and drops its own scratch
  database. The production database is never used.
- **RLS measures the direct-database / PostgREST boundary.** The FastAPI path
  connects with the service-role client, which carries `BYPASSRLS`, so RLS does
  not constrain application traffic today. That path is defended separately by
  explicit application-layer tenant scoping (M15) and is measured by the
  application-layer mutations.
- **M16 is verified at source level.** The harness performs a textual
  substitution in the frontend and does not run a frontend build, so it proves
  the guard against service-role exposure is live, not that the mutated
  frontend would compile.
- This verification measures whether the security suite can fail. It is not a
  penetration test, not a formal proof, and not a compliance certification.

### On M20

M20 exists to prove the WHERE-less sweep closes a real gap. With
`ai_recommendations_delete` widened to `USING (true)`, every test that existed
before the sweep still passes, because none issues a DELETE against
`ai_recommendations`, and a DELETE carrying a `WHERE` clause would be masked by
the SELECT policy anyway. Only
`TestWherelessWritesAcrossEveryTable` fails, in all four attacker scenarios.
