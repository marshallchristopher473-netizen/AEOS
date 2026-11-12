"""Build a fresh local database from the committed shim + migrations and seed
the same synthetic two-tenant fixture the RLS suite uses.

Usage: setup_db.py <backend_dir> <database_name> <authenticator_password>"""
import os
import sys
from pathlib import Path

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo

BACKEND = Path(sys.argv[1]).resolve()
DB = sys.argv[2]
ADMIN_URL = os.environ["AEOS_TEST_DATABASE_URL"]
AUTHENTICATOR_PASSWORD = sys.argv[3]

os.environ.setdefault("AEOS_REQUIRE_RLS_TESTS", "0")
sys.path.insert(0, str(BACKEND))
from tests.test_rls_enforcement import MIGRATIONS, SEED_SQL  # noqa: E402

with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
    conn.execute(
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s",
        (DB,),
    )
    conn.execute(f'DROP DATABASE IF EXISTS "{DB}"')
    conn.execute(f'CREATE DATABASE "{DB}"')

target = make_conninfo(**{**conninfo_to_dict(ADMIN_URL), "dbname": DB})
with psycopg.connect(target, autocommit=True) as conn:
    conn.execute((BACKEND / "tests" / "sql" / "supabase_shim.sql").read_text())
    for name in MIGRATIONS:
        conn.execute((BACKEND / "supabase" / "migrations" / name).read_text())
    conn.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role")
    conn.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role")
    conn.execute(SEED_SQL)
    conn.execute(f"ALTER ROLE authenticator PASSWORD '{AUTHENTICATOR_PASSWORD}'")
print(f"database {DB} ready: shim + {', '.join(MIGRATIONS)} + synthetic seed")
