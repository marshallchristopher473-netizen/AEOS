"""G1 WHERE-less UPDATE/DELETE sweep across every RLS-protected AEOS table.

Read-only against the candidate: imports the synthetic seed and identities
from the candidate's own test module, runs against a disposable PostgreSQL
database built from the candidate's migrations, and never touches tracked
files.

Each probe runs in a fresh database cloned from a migrated+seeded template,
so an attack that succeeds is committed and observed through a privileged
connection, not merely inferred from a row count.

Usage (disposable PostgreSQL 16 only, never a production database):

    export AEOS_TEST_DATABASE_URL=postgresql://postgres@localhost:5432/postgres
    python docs/evidence/g1/whereless_probe.py backend whereless-probe.json

Exit 0 only when no probe breaches org A and the positive control observes
every legitimate write; exit 1 otherwise.
"""
import json
import os
import sys
from pathlib import Path

import psycopg

if len(sys.argv) != 3:
    raise SystemExit("usage: whereless_probe.py <backend-dir> <output.json>")

ADMIN_URL = os.environ.get("AEOS_TEST_DATABASE_URL")
if not ADMIN_URL:
    raise SystemExit("AEOS_TEST_DATABASE_URL is not set; refusing to guess a database")

BACKEND = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(BACKEND))
from tests import test_rls_enforcement as t  # noqa: E402

TEMPLATE = "aeos_g1_probe_tmpl"

# One constant, non-column-referencing SET per table: the shape that never
# consults the SELECT policy, so only the UPDATE policy's USING clause gates it.
PROBE_COLUMN = {
    "students": "first_name",
    "assessments": "title",
    "intervention_plans": "title",
    "assessment_results": "summary",
    "ai_recommendations": "recommendation_text",
    "intervention_actions": "description",
    "schools": "name",
    "organizations": "name",
    "users": "full_name",
    "audit_logs": "action",
    "progress_events": "event_message",
}
MARKER = "G1-PROBE-PWNED"

AI_A = "0aaa0000-0000-4000-8000-0000000000a1"
AI_B = "0bbb0000-0000-4000-8000-0000000000b1"
ACT_A = "0aaa0000-0000-4000-8000-0000000000a2"
ACT_B = "0bbb0000-0000-4000-8000-0000000000b2"
LOG_A = "0aaa0000-0000-4000-8000-0000000000a3"
LOG_B = "0bbb0000-0000-4000-8000-0000000000b3"
EVT_A = "0aaa0000-0000-4000-8000-0000000000a4"
EVT_B = "0bbb0000-0000-4000-8000-0000000000b4"


def db_url(dbname):
    return ADMIN_URL.rsplit("/", 1)[0] + "/" + dbname


def admin(dbname="postgres"):
    return psycopg.connect(db_url(dbname), autocommit=True)


def build_template():
    with admin() as c:
        c.execute(f"DROP DATABASE IF EXISTS {TEMPLATE}")
        c.execute(f"CREATE DATABASE {TEMPLATE}")
    with admin(TEMPLATE) as c:
        c.execute(t.SHIM_SQL.read_text())
        for m in t.MIGRATIONS:
            c.execute((t.MIGRATIONS_DIR / m).read_text())
        c.execute(t.SEED_SQL)
        event_type = c.execute(
            "SELECT e.enumlabel FROM pg_enum e JOIN pg_type ty ON ty.oid = e.enumtypid "
            "JOIN pg_attribute a ON a.atttypid = ty.oid "
            "WHERE a.attrelid = 'public.progress_events'::regclass AND a.attname = 'event_type' "
            "ORDER BY e.enumsortorder LIMIT 1"
        ).fetchone()[0]
        c.execute(
            f"""
            INSERT INTO public.ai_recommendations
              (id, organization_id, assessment_id, created_by, model_name, recommendation_text) VALUES
              ('{AI_A}', '{t.ORG_A}', '{t.ASSESSMENT_A}', '{t.USER_A}', 'synthetic', 'Org A rec'),
              ('{AI_B}', '{t.ORG_B}', '{t.ASSESSMENT_B}', '{t.USER_B}', 'synthetic', 'Org B rec');
            INSERT INTO public.intervention_actions
              (id, intervention_plan_id, action_type, description) VALUES
              ('{ACT_A}', '{t.PLAN_A}', 'synthetic', 'Org A action'),
              ('{ACT_B}', '{t.PLAN_B}', 'synthetic', 'Org B action');
            INSERT INTO public.audit_logs
              (id, organization_id, entity_type, entity_id, action, performed_by) VALUES
              ('{LOG_A}', '{t.ORG_A}', 'student', '{t.STUDENT_A}', 'create', '{t.USER_A}'),
              ('{LOG_B}', '{t.ORG_B}', 'student', '{t.STUDENT_B}', 'create', '{t.USER_B}');
            INSERT INTO public.progress_events
              (id, organization_id, student_id, actor_id, event_type, event_message) VALUES
              ('{EVT_A}', '{t.ORG_A}', '{t.STUDENT_A}', '{t.USER_A}', '{event_type}', 'Org A event'),
              ('{EVT_B}', '{t.ORG_B}', '{t.STUDENT_B}', '{t.USER_B}', '{event_type}', 'Org B event');
            """
        )
        tables = [
            r[0]
            for r in c.execute(
                "SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relrowsecurity ORDER BY 1"
            )
        ]
    missing = set(tables) - set(PROBE_COLUMN)
    if missing:
        raise SystemExit(f"probe has no column mapping for RLS tables: {sorted(missing)}")
    return tables


def org_a_row_filter(table):
    if table == "organizations":
        return f"id = '{t.ORG_A}'"
    if table == "intervention_actions":
        return f"intervention_plan_id = '{t.PLAN_A}'"
    return f"organization_id = '{t.ORG_A}'"


def snapshot(dbname, table):
    """Privileged view of org A's rows for this table: (count, marker count)."""
    col = PROBE_COLUMN[table]
    with admin(dbname) as c:
        total = c.execute(f"SELECT count(*) FROM public.{table} WHERE {org_a_row_filter(table)}").fetchone()[0]
        marked = c.execute(
            f"SELECT count(*) FROM public.{table} WHERE {org_a_row_filter(table)} AND {col}::text = %s",
            (MARKER,),
        ).fetchone()[0]
    return total, marked


def probe(n, table, op, actor_auth, setup_sql):
    dbname = f"aeos_g1_probe_{n}"
    with admin() as c:
        c.execute(f"DROP DATABASE IF EXISTS {dbname}")
        c.execute(f"CREATE DATABASE {dbname} TEMPLATE {TEMPLATE}")
    try:
        if setup_sql:
            with admin(dbname) as c:
                c.execute(setup_sql)
        before_total, _ = snapshot(dbname, table)
        with psycopg.connect(db_url(dbname)) as actor:
            t._become(actor, actor_auth)
            role = actor.execute("SELECT current_user").fetchone()[0]
            assert role == "authenticated", role
            if op == "UPDATE":
                sql = f"UPDATE public.{table} SET {PROBE_COLUMN[table]} = %s"
                params = (MARKER,)
            else:
                sql = f"DELETE FROM public.{table}"
                params = None
            error = None
            try:
                cur = actor.execute(sql, params)
                rowcount = cur.rowcount
                actor.commit()
            except psycopg.Error as exc:
                actor.rollback()
                rowcount = 0
                error = type(exc).__name__
        after_total, marked = snapshot(dbname, table)
        breached = marked > 0 if op == "UPDATE" else after_total < before_total
        return {
            "table": table,
            "op": op,
            "statement": sql.replace("%s", f"'{MARKER}'"),
            "rowcount": rowcount,
            "error": error,
            "org_a_rows_before": before_total,
            "org_a_rows_after": after_total,
            "org_a_rows_marked": marked,
            "breached": breached,
        }
    finally:
        with admin() as c:
            c.execute(f"DROP DATABASE IF EXISTS {dbname}")


SCENARIOS = {
    # Org A suspended; its own admin (the most privileged in-tenant actor) attacks.
    "suspended_org_admin": (t.AUTH_ADMIN_A, f"UPDATE public.organizations SET status = 'suspended' WHERE id = '{t.ORG_A}'"),
    # Org A suspended; an ordinary teacher attacks.
    "suspended_org_teacher": (t.AUTH_A, f"UPDATE public.organizations SET status = 'suspended' WHERE id = '{t.ORG_A}'"),
    # Org A admin's own account deactivated.
    "inactive_admin_user": (t.AUTH_ADMIN_A, f"UPDATE public.users SET status = 'disabled' WHERE id = '{t.ADMIN_A}'"),
    # Active teacher in org B attacks org A (cross-tenant). Org B's own rows may change; org A's must not.
    "cross_tenant_teacher_b": (t.AUTH_B, None),
}

# Positive control: an ACTIVE org A admin legitimately writes org A rows. This
# proves the probe can observe a successful write, so "denied" above means the
# policy denied it rather than the harness failing to look.
CONTROL = ("positive_control_active_admin_a", t.AUTH_ADMIN_A, None)
CONTROL_TABLES_WITH_WRITE_POLICY = {
    "students", "assessments", "intervention_plans", "assessment_results",
    "ai_recommendations", "intervention_actions", "schools",
}


def main():
    tables = build_template()
    results = []
    n = 0
    for scenario, (actor, setup) in SCENARIOS.items():
        for table in tables:
            for op in ("UPDATE", "DELETE"):
                n += 1
                r = probe(n, table, op, actor, setup)
                r["scenario"] = scenario
                results.append(r)
                flag = "BREACH" if r["breached"] else "denied"
                print(f"{scenario:24} {op:6} {table:22} rowcount={r['rowcount']:<3} "
                      f"orgA {r['org_a_rows_before']}->{r['org_a_rows_after']} marked={r['org_a_rows_marked']} "
                      f"{('err=' + r['error']) if r['error'] else ''} {flag}")
    control_failures = []
    name, actor, setup = CONTROL
    for table in sorted(CONTROL_TABLES_WITH_WRITE_POLICY):
        for op in ("UPDATE", "DELETE"):
            n += 1
            r = probe(n, table, op, actor, setup)
            r["scenario"] = name
            observed = r["breached"]
            r["control_write_observed"] = observed
            r["breached"] = False
            results.append(r)
            if not observed:
                control_failures.append(f"{op} {table}")
            print(f"{name:24} {op:6} {table:22} rowcount={r['rowcount']:<3} "
                  f"orgA {r['org_a_rows_before']}->{r['org_a_rows_after']} marked={r['org_a_rows_marked']} "
                  f"{('err=' + r['error']) if r['error'] else ''} {'write observed' if observed else 'CONTROL FAILED'}")
    with admin() as c:
        c.execute(f"DROP DATABASE IF EXISTS {TEMPLATE}")
    print(f"control_failures={control_failures}")
    breaches = [r for r in results if r["breached"]]
    Path(sys.argv[2]).write_text(json.dumps({"probes": len(results), "breaches": len(breaches), "control_failures": control_failures, "results": results}, indent=2))
    print(f"\nprobes={len(results)} breaches={len(breaches)}")
    sys.exit(1 if breaches or control_failures else 0)


if __name__ == "__main__":
    main()
