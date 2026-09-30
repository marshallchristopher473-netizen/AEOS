"""Committed mutation suite for the AEOS multi-tenant security boundary.

WHY THIS EXISTS
---------------
A green security suite proves nothing unless it can fail. This module
deliberately breaks the tenant boundary one control at a time, runs the
relevant tests against the broken copy, and asserts that the suite NOTICES.
A mutation that survives is reported as SURVIVED and fails the run.

It exists as a committed, runnable artifact rather than an ad-hoc script
because the specific regression it guards against — replacing
`students_select` with `USING (true)`, which removes SELECT tenant isolation
entirely while leaving the policy *name* in place — is invisible to every
string- and regex-based test in this repository. `test_security_artifacts.py`
asserts `"CREATE POLICY students_select" in sql`, which such a mutation
satisfies exactly.

THE REPOSITORY IS NEVER MODIFIED. Each mutation is applied to a throwaway copy
of the repository under a temporary directory, which is deleted afterwards.

WHAT COUNTS AS A KILL
---------------------
A mutation is KILLED only when the mutated tree still builds and a *test
assertion* fails. Setup failures, import errors, syntax errors, collection
errors and migration failures are deliberately NOT counted as kills — they are
reported as INVALID, because a mutation the suite never actually executed
proves nothing about the suite. Every mutation therefore goes through an
explicit validity precheck before any test runs:

  * Python targets       -> byte-compile the tree and import `app.main`
  * SQL targets          -> apply the shim + migrations 001..004 to a scratch
                            database and require every statement to succeed
  * Frontend TS targets  -> textual substitution only (no build in this harness)

RUNNING
-------
    export AEOS_TEST_DATABASE_URL=postgresql://postgres@localhost:5432/postgres
    python -m tests.security_mutations

Exit code 0 means every behaviour-changing mutation was detected. Non-zero
means at least one security control can be removed without any test failing,
or a mutation could not be executed at all.

Mutations whose target suite needs a database are skipped, loudly, when
AEOS_TEST_DATABASE_URL is unset — and the run then exits non-zero, because a
mutation suite that silently skips its database half is exactly the failure
mode it is meant to prevent.

`--json PATH` writes the full machine-readable result matrix for audit.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND.parent
MIGRATIONS = "backend/supabase/migrations"
SHIM = "backend/tests/sql/supabase_shim.sql"

# Migration order must match tests/test_rls_enforcement.py.
MIGRATION_FILES = (
    "001_initial_schema.sql",
    "002_tenant_rls.sql",
    "003_fk_relationship_hardening.sql",
    "004_org_lifecycle_and_write_authority.sql",
)

# Target suites. DB-backed mutations must be checked against the enforcement
# suite; application-layer mutations are caught without a database.
RLS_SUITE = ("tests/test_rls_enforcement.py",)
ARTIFACT_SUITE = ("tests/test_security_artifacts.py",)
AUTH_SUITE = (
    "tests/test_auth.py",
    "tests/test_route_authentication.py",
    "tests/test_dependencies.py",
    "tests/test_authorization.py",
)
APP_SUITE = (
    "tests/test_students.py",
    "tests/test_assessments.py",
    "tests/test_assessment_results.py",
    "tests/test_intervention_plans.py",
    "tests/test_authorization.py",
    "tests/test_dependencies.py",
    "tests/test_route_authentication.py",
    "tests/test_auth.py",
    "tests/test_security_artifacts.py",
    "tests/test_fk_relationship_rls.py",
)
FULL_SUITE = ("tests/",)


class Mutation:
    def __init__(
        self,
        contract,
        name,
        boundary,
        path,
        old,
        new,
        suite,
        needs_db,
        equivalent_because=None,
    ):
        # Identifier from the requested M01..M18 mutation contract. Several
        # mutations may share an identifier when the contract line names one
        # boundary that this codebase enforces in more than one materially
        # distinct place (e.g. M18's seven separate JWT validation cases).
        self.contract = contract
        self.name = name
        # Plain-language statement of the security property being removed.
        self.boundary = boundary
        self.path = path
        self.old = old
        self.new = new
        self.suite = suite
        self.needs_db = needs_db
        # An "equivalent mutant" changes the source without changing observable
        # behaviour, so no test can detect it and none should be contrived to.
        # Set this ONLY with recorded evidence that the removed condition is
        # genuinely unreachable, and state the evidence in the string.
        self.equivalent_because = equivalent_because

    @property
    def kind(self):
        suffix = Path(self.path).suffix
        return {".py": "python", ".sql": "sql"}.get(suffix, "frontend")

    def apply(self, root):
        target = root / self.path
        text = target.read_text()
        occurrences = text.count(self.old)
        if occurrences == 0:
            raise AssertionError(
                f"{self.name}: anchor not found in {self.path}. The mutation is "
                f"stale — the code it targets has moved, so this mutation is no "
                f"longer proving anything."
            )
        # Exactly one expected production site. More than one means the anchor
        # is ambiguous: `replace(..., 1)` would silently mutate whichever came
        # first, so the mutation would no longer describe what it claims to
        # test, and a kill could be attributed to the wrong control.
        if occurrences != 1:
            raise AssertionError(
                f"{self.name}: anchor matches {occurrences} sites in "
                f"{self.path}, expected exactly 1. The mutation is ambiguous "
                f"and cannot be attributed to a single control."
            )
        target.write_text(text.replace(self.old, self.new, 1))


MUTATIONS = [
    # =====================================================================
    # M01 — remove or bypass the authentication dependency
    # =====================================================================
    Mutation(
        "M01",
        "authentication dependency replaced by a constant subject",
        "Every business route must require a verified bearer token; the "
        "identity chain must begin at get_current_user and nowhere else.",
        "backend/app/core/dependencies.py",
        "async def get_db_user(\n"
        "    user_payload: dict = Depends(get_current_user),",
        "async def get_db_user(\n"
        '    user_payload: dict = Depends(lambda: {"sub": "auth-user-a"}),',
        APP_SUITE,
        False,
    ),
    # =====================================================================
    # M02 — bypass JWT verification entirely
    # =====================================================================
    Mutation(
        "M02",
        "JWT verification bypassed: claims read without decoding",
        "Claims may only be trusted after signature, expiry, issuer and "
        "audience verification against the published JWKS.",
        "backend/app/core/auth.py",
        "        payload = jwt.decode(\n"
        "            token,\n"
        "            matching_key,\n"
        "            algorithms=[algorithm],\n"
        "            audience=SUPABASE_JWT_AUDIENCE,\n"
        "            issuer=SUPABASE_JWT_ISSUER,\n"
        "            options={\n"
        '                "verify_signature": True,\n'
        '                "verify_exp": True,\n'
        '                "verify_aud": True,\n'
        '                "verify_iss": True,\n'
        "            },\n"
        "        )",
        "        payload = jwt.get_unverified_claims(token)",
        APP_SUITE,
        False,
    ),
    # =====================================================================
    # M03 — replace the authenticated actor with a client-provided user_id
    # =====================================================================
    Mutation(
        "M03",
        "client-provided user_id claim overrides the resolved actor identity",
        "Actor identity is the database user row selected by the verified "
        "`sub`; no other token field may name the actor.",
        "backend/app/core/dependencies.py",
        "    db_user = response.data[0]\n",
        "    db_user = dict(response.data[0])\n"
        '    if isinstance(user_payload.get("user_id"), str):\n'
        '        db_user["id"] = user_payload["user_id"]\n',
        APP_SUITE,
        False,
    ),
    # =====================================================================
    # M04 — accept a client-provided organization_id as authority
    # =====================================================================
    Mutation(
        "M04",
        "client-provided organization_id claim overrides tenant authority",
        "Tenant authority is derived server-side from the user row; a token "
        "claim must never select the organization.",
        "backend/app/core/dependencies.py",
        "    db_user = response.data[0]\n",
        "    db_user = dict(response.data[0])\n"
        '    if isinstance(user_payload.get("organization_id"), str):\n'
        '        db_user["organization_id"] = user_payload["organization_id"]\n',
        APP_SUITE,
        False,
    ),
    # =====================================================================
    # M05-M08 — cross-tenant SELECT isolation in the database
    # The specific regression this suite was created to catch.
    # =====================================================================
    Mutation(
        "M05",
        "students_select becomes globally permissive: USING (true)",
        "A member of one organization must not SELECT another organization's "
        "student rows.",
        f"{MIGRATIONS}/002_tenant_rls.sql",
        "CREATE POLICY students_select\n"
        "ON public.students FOR SELECT TO authenticated\n"
        "USING (public.aeos_has_org_access(organization_id));",
        "CREATE POLICY students_select\n"
        "ON public.students FOR SELECT TO authenticated\n"
        "USING (true);",
        RLS_SUITE,
        True,
    ),
    Mutation(
        "M06",
        "assessments_select becomes globally permissive: USING (true)",
        "A member of one organization must not SELECT another organization's "
        "assessment rows.",
        f"{MIGRATIONS}/002_tenant_rls.sql",
        "CREATE POLICY assessments_select\n"
        "ON public.assessments FOR SELECT TO authenticated\n"
        "USING (public.aeos_has_org_access(organization_id));",
        "CREATE POLICY assessments_select\n"
        "ON public.assessments FOR SELECT TO authenticated\n"
        "USING (true);",
        RLS_SUITE,
        True,
    ),
    Mutation(
        "M07",
        "intervention_plans_select becomes globally permissive: USING (true)",
        "A member of one organization must not SELECT another organization's "
        "intervention plans.",
        f"{MIGRATIONS}/002_tenant_rls.sql",
        "CREATE POLICY intervention_plans_select\n"
        "ON public.intervention_plans FOR SELECT TO authenticated\n"
        "USING (public.aeos_has_org_access(organization_id));",
        "CREATE POLICY intervention_plans_select\n"
        "ON public.intervention_plans FOR SELECT TO authenticated\n"
        "USING (true);",
        RLS_SUITE,
        True,
    ),
    Mutation(
        "M08",
        "assessment_results_select becomes globally permissive: USING (true)",
        "A member of one organization must not SELECT another organization's "
        "assessment results.",
        f"{MIGRATIONS}/003_fk_relationship_hardening.sql",
        "CREATE POLICY assessment_results_select\n"
        "ON public.assessment_results FOR SELECT TO authenticated\n"
        "USING (public.aeos_has_org_access(assessment_results.organization_id));",
        "CREATE POLICY assessment_results_select\n"
        "ON public.assessment_results FOR SELECT TO authenticated\n"
        "USING (true);",
        RLS_SUITE,
        True,
    ),
    # =====================================================================
    # M09 — organization lifecycle (suspension) must remove access
    # =====================================================================
    Mutation(
        "M09",
        "aeos_has_org_access stops requiring an ACTIVE organization",
        "Suspending an organization must immediately remove read access "
        "through RLS.",
        f"{MIGRATIONS}/004_org_lifecycle_and_write_authority.sql",
        "          AND membership.organization_id = target_organization_id\n"
        "          AND membership.status = 'active'\n"
        "          AND tenant.status = 'active'\n"
        "    );\n"
        "$$;\n"
        "\n"
        "CREATE OR REPLACE FUNCTION public.aeos_can_write_org",
        "          AND membership.organization_id = target_organization_id\n"
        "          AND membership.status = 'active'\n"
        "    );\n"
        "$$;\n"
        "\n"
        "CREATE OR REPLACE FUNCTION public.aeos_can_write_org",
        RLS_SUITE,
        True,
    ),
    Mutation(
        "M09",
        "aeos_can_write_org stops requiring an ACTIVE organization",
        "Suspending an organization must immediately remove write authority "
        "through RLS.",
        f"{MIGRATIONS}/004_org_lifecycle_and_write_authority.sql",
        "          AND membership.status = 'active'\n"
        "          AND tenant.status = 'active'\n"
        "          AND membership.role IN ('teacher', 'admin')",
        "          AND membership.status = 'active'\n"
        "          AND membership.role IN ('teacher', 'admin')",
        RLS_SUITE,
        True,
        # NOT EQUIVALENT. This mutant was previously excluded from the score as
        # a proved-equivalent mutant. Independent verification refuted that: the
        # equivalence proof's reasoning held only for statements carrying a
        # WHERE or RETURNING clause. PostgreSQL applies a table's SELECT policy
        # to an UPDATE only when the statement must locate rows, so a WHERE-less
        # `UPDATE students SET ...` never consults `aeos_has_org_access` and
        # `students_update`'s USING clause — `aeos_can_write_org` alone —
        # becomes the only control. All 20 probes in that proof used WHERE, so
        # all 20 were masked. Against a suspended tenant the mutant produces
        # `UPDATE 1` and persists the changed value.
        #
        # Killed behaviourally by
        # tests/test_rls_enforcement.py::TestOrganizationLifecycle::
        # test_suspended_organization_cannot_update_without_a_where_clause,
        # and scored in the denominator like every other valid mutant.
    ),
    Mutation(
        "M09",
        "aeos_is_org_admin stops requiring an ACTIVE organization",
        "Suspending an organization must immediately remove admin authority "
        "through RLS.",
        f"{MIGRATIONS}/004_org_lifecycle_and_write_authority.sql",
        "          AND membership.status = 'active'\n"
        "          AND tenant.status = 'active'\n"
        "          AND membership.role = 'admin'",
        "          AND membership.status = 'active'\n"
        "          AND membership.role = 'admin'",
        RLS_SUITE,
        True,
    ),
    Mutation(
        "M09",
        "actor resolution stops requiring an ACTIVE organization",
        "Suspending an organization must immediately remove access on the "
        "FastAPI request path, which uses the RLS-bypassing service role.",
        "backend/app/core/dependencies.py",
        '.eq("id", db_user["organization_id"])\n        .eq("status", "active")',
        '.eq("id", db_user["organization_id"])',
        APP_SUITE,
        False,
    ),
    # =====================================================================
    # M10 — membership lifecycle must remove access
    # =====================================================================
    Mutation(
        "M10",
        "aeos_has_org_access stops requiring an ACTIVE membership",
        "Deactivating a membership must immediately remove access through RLS.",
        f"{MIGRATIONS}/004_org_lifecycle_and_write_authority.sql",
        # Anchored through the end of the function and into the NEXT function's
        # header. Without that tail this prefix matches all four `aeos_*`
        # helpers in 004, and the mutation would silently hit whichever came
        # first rather than the one it names.
        "          AND membership.organization_id = target_organization_id\n"
        "          AND membership.status = 'active'\n"
        "          AND tenant.status = 'active'\n"
        "    );\n"
        "$$;\n"
        "\n"
        "CREATE OR REPLACE FUNCTION public.aeos_can_write_org",
        "          AND membership.organization_id = target_organization_id\n"
        "          AND tenant.status = 'active'\n"
        "    );\n"
        "$$;\n"
        "\n"
        "CREATE OR REPLACE FUNCTION public.aeos_can_write_org",
        RLS_SUITE,
        True,
    ),
    Mutation(
        "M10",
        "actor resolution accepts inactive users",
        "A disabled user must not resolve to an actor on the FastAPI request "
        "path.",
        "backend/app/core/dependencies.py",
        '.eq("auth_user_id", auth_user_id)\n        .eq("status", "active")',
        '.eq("auth_user_id", auth_user_id)',
        APP_SUITE,
        False,
    ),
    # =====================================================================
    # M11 — write authority / role escalation
    # =====================================================================
    Mutation(
        "M11",
        "students_delete widened from admin back to any teacher",
        "DELETE of a student is reserved to organization admins.",
        f"{MIGRATIONS}/004_org_lifecycle_and_write_authority.sql",
        "CREATE POLICY students_delete\n"
        "ON public.students FOR DELETE TO authenticated\n"
        "USING (public.aeos_is_org_admin(students.organization_id));",
        "CREATE POLICY students_delete\n"
        "ON public.students FOR DELETE TO authenticated\n"
        "USING (public.aeos_can_write_org(students.organization_id));",
        RLS_SUITE,
        True,
    ),
    # =====================================================================
    # M12 — INSERT actor binding
    # =====================================================================
    Mutation(
        "M12",
        "students_insert drops the created_by actor binding",
        "An inserted row must record the acting user; created_by may not name "
        "another user.",
        f"{MIGRATIONS}/003_fk_relationship_hardening.sql",
        # Anchored from the policy header: 003 defines students_insert and
        # students_update with byte-identical WITH CHECK bodies, so the body
        # alone matches both and would mutate whichever came first.
        "CREATE POLICY students_insert\n"
        "ON public.students FOR INSERT TO authenticated\n"
        "WITH CHECK (\n"
        "    public.aeos_can_write_org(students.organization_id)\n"
        "    AND public.aeos_is_current_actor_for_org(\n"
        "        students.created_by,\n"
        "        students.organization_id\n"
        "    )\n"
        "    AND (\n"
        "        students.school_id IS NULL",
        "CREATE POLICY students_insert\n"
        "ON public.students FOR INSERT TO authenticated\n"
        "WITH CHECK (\n"
        "    public.aeos_can_write_org(students.organization_id)\n"
        "    AND (\n"
        "        students.school_id IS NULL",
        RLS_SUITE,
        True,
    ),
    # =====================================================================
    # M13 — foreign-key tenant containment
    # =====================================================================
    Mutation(
        "M13",
        "assessments_insert FK tenant check collapsed to a tautology",
        "An assessment may only reference a student in the same organization.",
        f"{MIGRATIONS}/003_fk_relationship_hardening.sql",
        "        WHERE related_student.id = assessments.student_id\n"
        "          AND related_student.organization_id = assessments.organization_id\n"
        "    )\n"
        ");\n"
        "\n"
        "DROP POLICY IF EXISTS assessments_update",
        "        WHERE related_student.id = related_student.id\n"
        "          AND related_student.organization_id = related_student.organization_id\n"
        "    )\n"
        ");\n"
        "\n"
        "DROP POLICY IF EXISTS assessments_update",
        RLS_SUITE,
        True,
    ),
    # =====================================================================
    # M14 — ownership immutability
    # =====================================================================
    Mutation(
        "M14",
        "ownership columns become mutable (identity trigger neutered)",
        "organization_id and created_by may never be changed by an UPDATE.",
        f"{MIGRATIONS}/003_fk_relationship_hardening.sql",
        "    IF NEW.organization_id IS DISTINCT FROM OLD.organization_id\n"
        "       OR NEW.created_by IS DISTINCT FROM OLD.created_by THEN",
        "    IF FALSE THEN",
        RLS_SUITE,
        True,
    ),
    # =====================================================================
    # M15 — application-layer tenant scoping of the service-role client
    # =====================================================================
    Mutation(
        "M15",
        "list endpoint drops its tenant filter",
        "Every service-role query must carry the server-derived "
        "organization_id; list endpoints must not return other tenants' rows.",
        "backend/app/services/tenant_scope.py",
        '.select("*")\n        .eq("organization_id", organization_id)\n        .execute()',
        '.select("*")\n        .execute()',
        APP_SUITE,
        False,
    ),
    Mutation(
        "M15",
        "get-by-id endpoint drops its tenant filter",
        "Every service-role query must carry the server-derived "
        "organization_id; fetch-by-id must not expose another tenant's row.",
        "backend/app/services/tenant_scope.py",
        '.eq("id", row_id)\n        .eq("organization_id", organization_id)\n        .limit(1)',
        '.eq("id", row_id)\n        .limit(1)',
        APP_SUITE,
        False,
    ),
    # =====================================================================
    # M16 — service-role authority trusted for an ordinary request
    # =====================================================================
    Mutation(
        "M16",
        "browser falls back to the service-role key when no user token is present",
        "The service-role credential bypasses RLS and must never be reachable "
        "from an ordinary (browser) request; only a user bearer token may "
        "authorize one.",
        "frontend/src/lib/api.ts",
        "      ...(token ? { Authorization: `Bearer ${token}` } : {}),",
        "      ...(token\n"
        "        ? { Authorization: `Bearer ${token}` }\n"
        "        : { Authorization: `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}` }),",
        ARTIFACT_SUITE,
        False,
    ),
    # =====================================================================
    # M17 — permissive authentication / authorization default
    # =====================================================================
    Mutation(
        "M17",
        "missing credentials fall through to a default authenticated subject",
        "Absent or non-bearer credentials must fail closed with 401, never "
        "resolve to a default identity.",
        "backend/app/core/auth.py",
        '        raise unauthorized("Not authenticated")',
        '        return {"sub": "auth-user-a"}',
        APP_SUITE,
        False,
    ),
    Mutation(
        "M17",
        "role authorization always allows",
        "Role authorization must deny by default; an actor outside the allow "
        "list may not perform a privileged write.",
        "backend/app/core/dependencies.py",
        "if actor.role not in allowed_roles:",
        "if False:",
        APP_SUITE,
        False,
    ),
    # =====================================================================
    # M18 — weakened JWT validation, one case per rejected-token property
    # =====================================================================
    Mutation(
        "M18a",
        "expired tokens accepted (verify_exp disabled)",
        "An expired token must be rejected.",
        "backend/app/core/auth.py",
        '                "verify_exp": True,',
        '                "verify_exp": False,',
        APP_SUITE,
        False,
    ),
    Mutation(
        "M18b",
        "wrong issuer accepted (verify_iss disabled)",
        "A token issued by anyone other than the configured Supabase issuer "
        "must be rejected.",
        "backend/app/core/auth.py",
        '                "verify_iss": True,',
        '                "verify_iss": False,',
        APP_SUITE,
        False,
    ),
    Mutation(
        "M18c",
        "audience validation removed (wrong or absent audience accepted)",
        "A token minted for another audience, or carrying no audience claim at "
        "all, must be rejected.",
        "backend/app/core/auth.py",
        # Audience is enforced in TWO places, so the mutation must remove both
        # to represent the boundary the contract names. Targeting only
        # `"verify_aud": True` proves nothing: the explicit check below strictly
        # subsumes it (jose 3.3.0 returns early from `_validate_aud` when the
        # claim is absent), so flipping the flag alone changes no observable
        # behaviour and the mutant would survive forever as a dead control.
        '                "verify_aud": True,\n'
        '                "verify_iss": True,\n'
        "            },\n"
        "        )\n"
        "        # python-jose 3.3.0 returns early from `_validate_aud` when the `aud`\n"
        "        # claim is absent, so `verify_aud: True` above rejects a WRONG audience\n"
        "        # but silently accepts a MISSING one. Configuring an audience expresses\n"
        "        # the intent that audience be enforced, so require the claim here.\n"
        "        # This only ever rejects: no audience is inserted, inferred or defaulted.\n"
        "        audience = payload.get(\"aud\")\n"
        "        if audience is None:\n"
        '            raise unauthorized("JWT is missing the audience claim")\n'
        "        presented = audience if isinstance(audience, (list, tuple)) else [audience]\n"
        "        if SUPABASE_JWT_AUDIENCE not in presented:\n"
        '            raise unauthorized("JWT audience is not accepted")\n',
        '                "verify_aud": False,\n'
        '                "verify_iss": True,\n'
        "            },\n"
        "        )\n",
        APP_SUITE,
        False,
    ),
    Mutation(
        "M18d",
        "invalid signature accepted (verify_signature disabled)",
        "A token not signed by a published Supabase key must be rejected.",
        "backend/app/core/auth.py",
        '                "verify_signature": True,',
        '                "verify_signature": False,',
        APP_SUITE,
        False,
    ),
    Mutation(
        "M18i",
        "symmetric (oct) published keys accepted as HS256",
        "A shared secret must never verify a token, even one published in the "
        "JWKS; otherwise anyone who can read the JWKS can mint any session.",
        "backend/app/core/auth.py",
        '    elif key_type == "EC" and jwk.get("crv") == "P-256":\n'
        '        algorithm = "ES256"\n',
        '    elif key_type == "EC" and jwk.get("crv") == "P-256":\n'
        '        algorithm = "ES256"\n'
        '    elif key_type == "oct":\n'
        '        algorithm = "HS256"\n',
        APP_SUITE,
        False,
    ),
    Mutation(
        "M18j",
        "verification algorithm taken from the token header",
        "The algorithm is pinned by the published key the `kid` selects; the "
        "token's own `alg` header may not choose it.",
        "backend/app/core/auth.py",
        "            algorithms=[algorithm],\n",
        '            algorithms=[unverified_header.get("alg")],\n',
        APP_SUITE,
        False,
    ),
    Mutation(
        "M18e",
        "missing key ID falls back to the first published key",
        "A token whose header carries no `kid` must be rejected; the "
        "verification key may not be guessed.",
        "backend/app/core/auth.py",
        '        kid = unverified_header.get("kid")\n'
        "        if not isinstance(kid, str) or not kid:\n"
        '            raise unauthorized("JWT is missing a key ID")',
        '        kid = unverified_header.get("kid")\n'
        "        if not isinstance(kid, str) or not kid:\n"
        "            kid = next(\n"
        '                (k.get("kid") for k in (await get_jwks()).get("keys", [])),\n'
        "                None,\n"
        "            )",
        APP_SUITE,
        False,
    ),
    Mutation(
        "M18f",
        "unknown key ID falls back to the first published key",
        "A token whose `kid` matches no published key must be rejected; "
        "otherwise key rotation and revocation are meaningless.",
        "backend/app/core/auth.py",
        "        if matching_key is None:\n"
        '            raise unauthorized("JWT signing key is unknown")',
        "        if matching_key is None:\n"
        "            matching_key = next(\n"
        '                iter((await get_jwks()).get("keys", [])), None\n'
        "            )",
        APP_SUITE,
        False,
    ),
    Mutation(
        "M18g",
        "malformed tokens fall through to a default authenticated subject",
        "Any JWT parse or validation error must fail closed with 401; the "
        "error path may not return an identity.",
        "backend/app/core/auth.py",
        "    except (JOSEError, ValueError, TypeError) as exc:\n"
        "        raise unauthorized() from exc",
        "    except (JOSEError, ValueError, TypeError):\n"
        '        return {"sub": "auth-user-a"}',
        APP_SUITE,
        False,
    ),
]


# ---------------------------------------------------------------------------
# Validity prechecks. A mutation that does not build was never executed, so it
# must not be scored as killed.
# ---------------------------------------------------------------------------


def _precheck(root, mutation, database_url):
    """Return (ok, detail). `ok is False` means the mutant is INVALID."""
    backend = root / "backend"

    if mutation.kind == "python":
        compiled = subprocess.run(
            [sys.executable, "-m", "compileall", "-q", "app", "tests"],
            cwd=backend, capture_output=True, text=True, timeout=300,
        )
        if compiled.returncode != 0:
            return False, f"byte-compilation failed: {compiled.stderr.strip()[:400]}"

        imported = subprocess.run(
            [sys.executable, "-c", "from app.main import app; print(len(app.routes))"],
            cwd=backend, capture_output=True, text=True, timeout=300,
        )
        if imported.returncode != 0:
            return False, f"app import failed: {imported.stderr.strip()[:400]}"
        return True, f"compiles; app imports with {imported.stdout.strip()} routes"

    if mutation.kind == "sql":
        if not database_url:
            return False, "no database configured for SQL validity precheck"
        try:
            import psycopg
        except ImportError:  # pragma: no cover - dependency is declared
            return False, "psycopg unavailable for SQL validity precheck"

        db_name = f"aeos_mutchk_{uuid.uuid4().hex[:12]}"
        from psycopg.conninfo import conninfo_to_dict, make_conninfo

        params = conninfo_to_dict(database_url)
        params["dbname"] = db_name
        target = make_conninfo(**params)
        try:
            with psycopg.connect(database_url, autocommit=True) as conn:
                conn.execute(f'CREATE DATABASE "{db_name}"')
            with psycopg.connect(target, autocommit=True) as conn:
                conn.execute((root / SHIM).read_text())
                for name in MIGRATION_FILES:
                    conn.execute((root / MIGRATIONS / name).read_text())
        except Exception as exc:  # noqa: BLE001 - reported, not swallowed
            return False, f"migrations 001..004 failed to apply: {exc}"
        finally:
            try:
                with psycopg.connect(database_url, autocommit=True) as conn:
                    conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
            except Exception:  # noqa: BLE001 - cleanup only
                pass
        return True, "migrations 001..004 apply cleanly"

    return True, "textual substitution (no build step in this harness)"


def _run_suite(root, suite, database_url):
    env = dict(os.environ)
    if database_url:
        env["AEOS_TEST_DATABASE_URL"] = database_url
    else:
        env.pop("AEOS_TEST_DATABASE_URL", None)
    env.pop("AEOS_REQUIRE_RLS_TESTS", None)
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", *suite, "-q", "--no-header",
         "-p", "no:cacheprovider", "--tb=line", "-rfE"],
        cwd=root / "backend", env=env, capture_output=True, text=True, timeout=1800,
    )
    lines = completed.stdout.strip().splitlines()
    summary = ""
    for line in reversed(lines):
        if "passed" in line or "failed" in line or "error" in line:
            summary = line.strip()
            break
    failed = [ln.strip() for ln in lines if ln.startswith("FAILED ")]
    errored = [ln.strip() for ln in lines if ln.startswith("ERROR ")]
    return completed.returncode, summary, failed, errored


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", dest="json_path", default=None,
                        help="write the full result matrix to this path")
    args = parser.parse_args(argv)

    database_url = os.environ.get("AEOS_TEST_DATABASE_URL")
    print("AEOS security mutation suite")
    print(f"repository: {REPO_ROOT}")
    print(f"database  : {'configured' if database_url else 'NOT CONFIGURED'}")
    print(f"mutations : {len(MUTATIONS)}")
    print()

    records = []

    for mutation in MUTATIONS:
        record = {
            "contract": mutation.contract,
            "name": mutation.name,
            "boundary": mutation.boundary,
            "path": mutation.path,
            "suite": list(mutation.suite),
            "equivalent_because": mutation.equivalent_because,
            "result": None,
            "precheck": None,
            "subset_summary": None,
            "killed_by": [],
            "full_suite_summary": None,
            "seconds": None,
        }

        if mutation.needs_db and not database_url:
            record["result"] = "NOT EXECUTED"
            record["precheck"] = "skipped: no database configured"
            records.append(record)
            print(f"[NOT RUN ] {mutation.contract} {mutation.name}")
            continue

        started = time.time()
        workdir = Path(tempfile.mkdtemp(prefix="aeos_mut_"))
        root = workdir / "repo"
        try:
            shutil.copytree(
                REPO_ROOT, root,
                ignore=shutil.ignore_patterns(
                    "__pycache__", ".pytest_cache", ".git", "node_modules",
                    ".next", "*.pyc",
                ),
            )
            try:
                mutation.apply(root)
            except AssertionError as exc:
                record["result"] = "INVALID MUTATION"
                record["precheck"] = f"stale anchor: {exc}"
                records.append(record)
                print(f"[INVALID ] {mutation.contract} {exc}")
                continue

            ok, detail = _precheck(root, mutation, database_url)
            record["precheck"] = detail
            if not ok:
                record["result"] = "INVALID MUTATION"
                records.append(record)
                print(f"[INVALID ] {mutation.contract} {mutation.name} -> {detail}")
                continue

            code, summary, failed, errored = _run_suite(
                root, mutation.suite, database_url if mutation.needs_db else None
            )
            record["subset_summary"] = summary
            record["killed_by"] = failed
            record["errors"] = errored

            # A kill must come from a failing test assertion. Collection
            # errors, import errors and setup errors are explicitly not kills.
            if failed:
                record["result"] = (
                    "KILLED" if not mutation.equivalent_because else "KILLED (was documented equivalent)"
                )
            elif errored or code not in (0, 1):
                record["result"] = "INVALID MUTATION"
                record["precheck"] = (
                    f"{detail}; but the suite did not execute cleanly "
                    f"(exit {code}): {summary}"
                )
            elif mutation.equivalent_because:
                record["result"] = "EQUIVALENT"
            else:
                record["result"] = "SURVIVED"

            # Interaction check: the complete suite, for every mutation that
            # got as far as executing.
            if database_url:
                _, full_summary, full_failed, _ = _run_suite(
                    root, FULL_SUITE, database_url
                )
                record["full_suite_summary"] = full_summary
                record["full_suite_failed_count"] = len(full_failed)

            record["seconds"] = round(time.time() - started, 1)
            records.append(record)

            tag = {
                "KILLED": "killed  ",
                "KILLED (was documented equivalent)": "killed* ",
                "EQUIVALENT": "equiv   ",
                "SURVIVED": "SURVIVED",
                "INVALID MUTATION": "INVALID ",
            }[record["result"]]
            print(f"[{tag}] {mutation.contract} {mutation.name}")
            print(f"           subset: {summary}")
            if failed:
                for node in failed[:4]:
                    print(f"           killed by: {node}")
                if len(failed) > 4:
                    print(f"           ... and {len(failed) - 4} more failing tests")
            if record["full_suite_summary"]:
                print(f"           full suite: {record['full_suite_summary']}")
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    killed = [r for r in records if r["result"].startswith("KILLED")]
    survived = [r for r in records if r["result"] == "SURVIVED"]
    equivalent = [r for r in records if r["result"] == "EQUIVALENT"]
    invalid = [r for r in records if r["result"] == "INVALID MUTATION"]
    not_executed = [r for r in records if r["result"] == "NOT EXECUTED"]

    denominator = len(killed) + len(survived)
    score = (len(killed) / denominator * 100) if denominator else 0.0

    print()
    print("=" * 72)
    print("MUTATION MATRIX")
    print("=" * 72)
    print(f"{'ID':<6} {'RESULT':<34} BOUNDARY")
    for record in records:
        print(f"{record['contract']:<6} {record['result']:<34} {record['name']}")

    print()
    print(f"killed           : {len(killed)}")
    print(f"survived         : {len(survived)}")
    print(f"equivalent       : {len(equivalent)}")
    print(f"invalid          : {len(invalid)}")
    print(f"not executed     : {len(not_executed)}")
    print(f"mutation score   : {len(killed)}/{denominator} = {score:.1f}%")

    if equivalent:
        print("\nEQUIVALENT (expected undetected — no behaviour change to detect):")
        for record in equivalent:
            print(f"  - {record['contract']} {record['name']}")
            print(f"    {record['equivalent_because']}")

    newly_detected = [
        r for r in records if r["result"] == "KILLED (was documented equivalent)"
    ]
    if newly_detected:
        print("\nNOTE — a mutation documented as equivalent is now DETECTED. That "
              "is not a failure, but the recorded justification is out of date "
              "and should be re-checked or the flag removed:")
        for record in newly_detected:
            print(f"  - {record['contract']} {record['name']}")

    failed_run = False
    if survived:
        failed_run = True
        print("\nSURVIVED — these security controls can be removed without any "
              "test failing:")
        for record in survived:
            print(f"  - {record['contract']} {record['name']}")
            print(f"    boundary: {record['boundary']}")
    if invalid:
        failed_run = True
        print("\nINVALID — these mutations never executed, so they prove nothing:")
        for record in invalid:
            print(f"  - {record['contract']} {record['name']}: {record['precheck']}")
    if not_executed:
        failed_run = True
        print("\nNOT EXECUTED for want of a database. A mutation suite that "
              "silently skips its database half is the failure mode it exists "
              "to prevent, so this is a failure:")
        for record in not_executed:
            print(f"  - {record['contract']} {record['name']}")

    if args.json_path:
        payload = {
            "repository_root": str(REPO_ROOT),
            "database_configured": bool(database_url),
            "python": sys.version,
            "totals": {
                "killed": len(killed),
                "survived": len(survived),
                "equivalent": len(equivalent),
                "invalid": len(invalid),
                "not_executed": len(not_executed),
                "score_numerator": len(killed),
                "score_denominator": denominator,
            },
            "mutations": records,
        }
        Path(args.json_path).write_text(json.dumps(payload, indent=2))
        print(f"\nwrote {args.json_path}")

    return 1 if failed_run else 0


if __name__ == "__main__":
    sys.exit(main())
