"""Committed mutation suite for the AEOS multi-tenant security boundary.

WHY THIS EXISTS
---------------
A green security suite proves nothing unless it can fail. This module
deliberately breaks the tenant boundary one control at a time, runs the
relevant tests against the broken copy, and asserts that the suite NOTICES.
A mutation that survives is reported as UNDETECTED and fails the run.

It exists as a committed, runnable artifact rather than an ad-hoc script
because the specific regression it guards against — replacing
`students_select` with `USING (true)`, which removes SELECT tenant isolation
entirely while leaving the policy *name* in place — is invisible to every
string- and regex-based test in this repository. `test_security_artifacts.py`
asserts `"CREATE POLICY students_select" in sql`, which such a mutation
satisfies exactly.

THE REPOSITORY IS NEVER MODIFIED. Each mutation is applied to a throwaway copy
of `backend/` under a temporary directory, which is deleted afterwards.

RUNNING
-------
    export AEOS_TEST_DATABASE_URL=postgresql://postgres@localhost:5432/postgres
    python -m tests.security_mutations

Exit code 0 means every mutation was detected. Non-zero means at least one
security control can be removed without any test failing.

Mutations whose target suite needs a database are skipped, loudly, when
AEOS_TEST_DATABASE_URL is unset — and the run then exits non-zero, because a
mutation suite that silently skips its database half is exactly the failure
mode it is meant to prevent.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
MIGRATIONS = "supabase/migrations"

# Target suites. DB-backed mutations must be checked against the enforcement
# suite; application-layer mutations are caught without a database.
RLS_SUITE = ("tests/test_rls_enforcement.py",)
APP_SUITE = (
    "tests/test_students.py",
    "tests/test_assessments.py",
    "tests/test_assessment_results.py",
    "tests/test_intervention_plans.py",
    "tests/test_authorization.py",
    "tests/test_dependencies.py",
    "tests/test_route_authentication.py",
)


class Mutation:
    def __init__(self, name, path, old, new, suite, needs_db, equivalent_because=None):
        self.name = name
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

    def apply(self, root):
        target = root / self.path
        text = target.read_text()
        if self.old not in text:
            raise AssertionError(
                f"{self.name}: anchor not found in {self.path}. The mutation is "
                f"stale — the code it targets has moved, so this mutation is no "
                f"longer proving anything."
            )
        target.write_text(text.replace(self.old, self.new, 1))


MUTATIONS = [
    # --- The specific regression this suite was created to catch -----------
    Mutation(
        "students_select becomes globally permissive: USING (true)",
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
        "assessments_select becomes globally permissive: USING (true)",
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
        "intervention_plans_select becomes globally permissive: USING (true)",
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
        "assessment_results_select becomes globally permissive: USING (true)",
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
    # --- Organization lifecycle (M1) ---------------------------------------
    Mutation(
        "aeos_has_org_access stops requiring an ACTIVE organization",
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
        "aeos_can_write_org stops requiring an ACTIVE organization",
        f"{MIGRATIONS}/004_org_lifecycle_and_write_authority.sql",
        "          AND membership.status = 'active'\n"
        "          AND tenant.status = 'active'\n"
        "          AND membership.role IN ('teacher', 'admin')",
        "          AND membership.status = 'active'\n"
        "          AND membership.role IN ('teacher', 'admin')",
        RLS_SUITE,
        True,
        equivalent_because=(
            "Redundant defence-in-depth in the current policy set, not a live "
            "control. Verified by applying ONLY this mutation against a "
            "suspended organization and attempting all 12 reachable writes as "
            "an authenticated teacher of that organization: students "
            "INSERT/UPDATE/DELETE, assessments INSERT/UPDATE, "
            "intervention_plans INSERT/UPDATE, assessment_results "
            "INSERT/UPDATE, intervention_actions INSERT, progress_events "
            "INSERT and ai_recommendations INSERT. The helper was confirmed "
            "live (aeos_can_write_org returned True for the suspended "
            "organization) and every write was still refused, because each "
            "path is independently gated by a helper that carries the same "
            "condition: INSERT paths by aeos_is_current_actor_for_org, and "
            "UPDATE/DELETE paths by aeos_has_org_access, since PostgreSQL "
            "applies the SELECT policy when locating rows for a WHERE clause. "
            "Re-verify this claim if any *_insert policy ever drops its actor "
            "binding, or if any write path stops reading an existing row."
        ),
    ),
    Mutation(
        "aeos_is_org_admin stops requiring an ACTIVE organization",
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
        "aeos_has_org_access stops requiring an ACTIVE membership",
        f"{MIGRATIONS}/004_org_lifecycle_and_write_authority.sql",
        "          AND membership.organization_id = target_organization_id\n"
        "          AND membership.status = 'active'\n"
        "          AND tenant.status = 'active'",
        "          AND membership.organization_id = target_organization_id\n"
        "          AND tenant.status = 'active'",
        RLS_SUITE,
        True,
    ),
    # --- Write authority (M2) ----------------------------------------------
    Mutation(
        "students_delete widened from admin back to any teacher",
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
    Mutation(
        "students_insert drops the created_by actor binding",
        f"{MIGRATIONS}/003_fk_relationship_hardening.sql",
        "    public.aeos_can_write_org(students.organization_id)\n"
        "    AND public.aeos_is_current_actor_for_org(\n"
        "        students.created_by,\n"
        "        students.organization_id\n"
        "    )\n"
        "    AND (\n"
        "        students.school_id IS NULL",
        "    public.aeos_can_write_org(students.organization_id)\n"
        "    AND (\n"
        "        students.school_id IS NULL",
        RLS_SUITE,
        True,
    ),
    Mutation(
        "assessments_insert FK tenant check collapsed to a tautology",
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
    Mutation(
        "ownership columns become mutable (identity trigger neutered)",
        f"{MIGRATIONS}/003_fk_relationship_hardening.sql",
        "    IF NEW.organization_id IS DISTINCT FROM OLD.organization_id\n"
        "       OR NEW.created_by IS DISTINCT FROM OLD.created_by THEN",
        "    IF FALSE THEN",
        RLS_SUITE,
        True,
    ),
    # --- Application layer --------------------------------------------------
    Mutation(
        "list endpoint drops its tenant filter",
        "app/services/tenant_scope.py",
        '.select("*")\n        .eq("organization_id", organization_id)\n        .execute()',
        '.select("*")\n        .execute()',
        APP_SUITE,
        False,
    ),
    Mutation(
        "get-by-id endpoint drops its tenant filter",
        "app/services/tenant_scope.py",
        '.eq("id", row_id)\n        .eq("organization_id", organization_id)\n        .limit(1)',
        '.eq("id", row_id)\n        .limit(1)',
        APP_SUITE,
        False,
    ),
    Mutation(
        "role authorization always allows",
        "app/core/dependencies.py",
        "if actor.role not in allowed_roles:",
        "if False:",
        APP_SUITE,
        False,
    ),
    Mutation(
        "actor resolution accepts inactive users",
        "app/core/dependencies.py",
        '.eq("auth_user_id", auth_user_id)\n        .eq("status", "active")',
        '.eq("auth_user_id", auth_user_id)',
        APP_SUITE,
        False,
    ),
    Mutation(
        "actor resolution stops requiring an ACTIVE organization",
        "app/core/dependencies.py",
        '.eq("id", db_user["organization_id"])\n        .eq("status", "active")',
        '.eq("id", db_user["organization_id"])',
        APP_SUITE,
        False,
    ),
]


def _run_suite(root, suite, database_url):
    env = dict(os.environ)
    if database_url:
        env["AEOS_TEST_DATABASE_URL"] = database_url
    else:
        env.pop("AEOS_TEST_DATABASE_URL", None)
    env.pop("AEOS_REQUIRE_RLS_TESTS", None)
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", *suite, "-q", "--no-header",
         "-p", "no:cacheprovider", "--tb=no"],
        cwd=root, env=env, capture_output=True, text=True, timeout=600,
    )
    summary = ""
    for line in reversed(completed.stdout.strip().splitlines()):
        if "passed" in line or "failed" in line or "error" in line:
            summary = line.strip()
            break
    return completed.returncode, summary


def main():
    database_url = os.environ.get("AEOS_TEST_DATABASE_URL")
    print("AEOS security mutation suite")
    print(f"backend : {BACKEND}")
    print(f"database: {'configured' if database_url else 'NOT CONFIGURED'}")
    print()

    undetected, stale, skipped, equivalent, newly_detected = [], [], [], [], []

    for mutation in MUTATIONS:
        if mutation.needs_db and not database_url:
            skipped.append(mutation.name)
            print(f"[SKIPPED ] {mutation.name}")
            continue

        workdir = Path(tempfile.mkdtemp(prefix="aeos_mut_"))
        root = workdir / "backend"
        try:
            shutil.copytree(
                BACKEND, root,
                ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"),
            )
            try:
                mutation.apply(root)
            except AssertionError as exc:
                stale.append(mutation.name)
                print(f"[STALE   ] {exc}")
                continue

            code, summary = _run_suite(
                root, mutation.suite, database_url if mutation.needs_db else None
            )
            if code == 0:
                if mutation.equivalent_because:
                    equivalent.append(mutation.name)
                    print(f"[equiv   ] {mutation.name}  ->  {summary}")
                else:
                    undetected.append(mutation.name)
                    print(f"[UNDETECT] {mutation.name}  ->  {summary}")
            else:
                if mutation.equivalent_because:
                    newly_detected.append(mutation.name)
                    print(f"[detected*] {mutation.name}  ->  {summary}")
                else:
                    print(f"[detected] {mutation.name}  ->  {summary}")
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    print()
    total = len(MUTATIONS)
    detected = total - len(undetected) - len(stale) - len(skipped) - len(equivalent)
    print(f"{detected}/{total - len(equivalent)} behaviour-changing mutations detected "
          f"({len(equivalent)} documented as equivalent)")

    if equivalent:
        print("\nEQUIVALENT (expected undetected — no behaviour change to detect):")
        for mutation in MUTATIONS:
            if mutation.name in equivalent:
                print(f"  - {mutation.name}")
                print(f"    {mutation.equivalent_because}")

    if newly_detected:
        print("\nNOTE — a mutation documented as equivalent is now DETECTED. That "
              "is not a failure, but the recorded justification is out of date "
              "and should be re-checked or the flag removed:")
        for name in newly_detected:
            print(f"  - {name}")

    failed = False
    if undetected:
        failed = True
        print("\nUNDETECTED — these security controls can be removed without any "
              "test failing:")
        for name in undetected:
            print(f"  - {name}")
    if stale:
        failed = True
        print("\nSTALE — these mutations no longer match the code and prove nothing:")
        for name in stale:
            print(f"  - {name}")
    if skipped:
        failed = True
        print("\nSKIPPED for want of a database. A mutation suite that silently "
              "skips its database half is the failure mode it exists to prevent, "
              "so this is a failure:")
        for name in skipped:
            print(f"  - {name}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
