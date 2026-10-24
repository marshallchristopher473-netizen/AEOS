"""End-to-end tenant-isolation checks (P0-01, re-run for P0-02).

Run via stack.sh (see README.md); every check must pass.

Path under test:  HTTP client -> AEOS FastAPI (uvicorn) -> supabase-py ->
PostgREST 12.2.3 -> PostgreSQL 16 (shim + every committed migration).
Second path:      HTTP client -> PostgREST directly (the path RLS governs).

All data is synthetic (seed from tests/test_rls_enforcement.py)."""
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

import httpx
import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from jose import jwt

H = Path(__file__).resolve().parent
BACKEND = H.parents[1]
WORK = Path(os.environ.get("AEOS_E2E_WORKDIR", H / ".work"))
sys.path.insert(0, str(BACKEND))
os.environ.setdefault("AEOS_REQUIRE_RLS_TESTS", "0")
import tests.test_rls_enforcement as S  # noqa: E402

API = "http://127.0.0.1:8000"
REST = "http://127.0.0.1:3001"
ISS = "http://127.0.0.1:54321/auth/v1"
ADMIN_URL = os.environ.get(
    "AEOS_TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)
DB_URL = make_conninfo(**{**conninfo_to_dict(ADMIN_URL), "dbname": os.environ.get("AEOS_E2E_DB", "aeos_e2e")})
ENV = dict(
    line.replace("export ", "").split("=", 1)
    for line in (WORK / "env.sh").read_text().splitlines()
)
ENV = {k: v.strip("'") for k, v in ENV.items()}
PRIV = (WORK / "rsa_private.pem").read_text()

results = []


def check(cid, requirement, ok, detail):
    results.append({"id": cid, "requirement": requirement, "pass": bool(ok), "detail": detail})
    print(f"{'PASS' if ok else 'FAIL'}  {cid:<5} {requirement} :: {detail}")


def token(sub, key=PRIV, kid="p0-01-local", **over):
    claims = {
        "sub": sub, "aud": "authenticated", "iss": ISS, "role": "authenticated",
        "exp": int(time.time()) + 600, "iat": int(time.time()),
    }
    claims.update(over)
    claims = {k: v for k, v in claims.items() if v is not None}
    return jwt.encode(claims, key, algorithm="RS256", headers={"kid": kid})


def bearer(t):
    return {"Authorization": f"Bearer {t}"}


def rest_jwt(sub):
    """A Supabase-style user access token as PostgREST would receive it."""
    return jwt.encode(
        {"sub": sub, "role": "authenticated", "aud": "authenticated",
         "exp": int(time.time()) + 600},
        ENV["PGRST_JWT_SECRET"], "HS256",
    )


def b_fingerprint():
    with psycopg.connect(DB_URL) as c:
        rows = []
        for t in ("students", "assessments", "intervention_plans", "assessment_results", "schools"):
            rows += [(t,) + tuple(r) for r in c.execute(
                f"SELECT * FROM public.{t} WHERE organization_id = %s ORDER BY id", (S.ORG_B,)
            ).fetchall()]
    return hashlib.sha256(repr(rows).encode()).hexdigest(), len(rows)


RES = {
    "students": ("/students", S.STUDENT_A, S.STUDENT_B),
    "assessments": ("/assessments", S.ASSESSMENT_A, S.ASSESSMENT_B),
    "intervention-plans": ("/intervention-plans", S.PLAN_A, S.PLAN_B),
    "assessment-results": ("/assessment-results", S.RESULT_A, S.RESULT_B),
}
B_IDS = {S.STUDENT_B, S.ASSESSMENT_B, S.PLAN_B, S.RESULT_B, S.ORG_B, S.SCHOOL_B}

c = httpx.Client(timeout=15, headers={"Connection": "close"})
A, B = bearer(token(S.AUTH_A)), bearer(token(S.AUTH_B))
fp_before = b_fingerprint()

# ---------------------------------------------------------------- U: unauthenticated
for name, (path, own, foreign) in RES.items():
    codes = [c.get(API + path).status_code, c.get(f"{API}{path}/{foreign}").status_code,
             c.post(API + path, json={}).status_code]
    check("U1", f"no token -> 401 on {name} list/get/create", codes == [401] * 3, codes)

rogue = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
bad = {
    "forged signature (same kid, attacker key)": token(S.AUTH_A, key=rogue),
    "unknown kid": token(S.AUTH_A, kid="nope"),
    "expired": token(S.AUTH_A, exp=int(time.time()) - 60),
    "wrong audience": token(S.AUTH_A, aud="anon"),
    "missing audience": token(S.AUTH_A, aud=None),
    "wrong issuer": token(S.AUTH_A, iss="https://evil.example/auth/v1"),
    "unknown subject": token(str(uuid.uuid4())),
    "garbage": "not-a-jwt",
}
for label, t in bad.items():
    code = c.get(API + "/students", headers=bearer(t)).status_code
    check("U2", f"{label} -> rejected", code in (401, 403), code)

# Direct PostgREST without any user identity (anon key / no key) must see nothing.
for tbl in ("students", "assessments", "intervention_plans", "assessment_results", "users", "organizations"):
    r1 = c.get(f"{REST}/{tbl}", headers={"apikey": ENV["SUPABASE_ANON_KEY"], **bearer(ENV["SUPABASE_ANON_KEY"])})
    r2 = c.get(f"{REST}/{tbl}")
    ok = all(r.status_code in (401, 403) or (r.status_code == 200 and r.json() == []) for r in (r1, r2))
    check("U3", f"direct PostgREST anon/no-key -> no {tbl} rows", ok,
          [(r.status_code, len(r.json()) if r.status_code == 200 else r.json().get("code")) for r in (r1, r2)])

# ---------------------------------------------------------------- X: cross-tenant via API
for name, (path, own, foreign) in RES.items():
    ra, rb = c.get(API + path, headers=A), c.get(API + path, headers=B)
    ids_a = {x["id"] for x in ra.json()} if ra.status_code == 200 else None
    ids_b = {x["id"] for x in rb.json()} if rb.status_code == 200 else None
    orgs_a = {x["organization_id"] for x in ra.json()} if ra.status_code == 200 else None
    check("X1", f"A lists {name}: only org A rows", ra.status_code == 200 and orgs_a <= {S.ORG_A}
          and own in ids_a and not (ids_a & B_IDS), {"status": ra.status_code, "orgs": sorted(orgs_a or [])})
    check("X1", f"B lists {name}: only org B rows", rb.status_code == 200 and own not in ids_b
          and foreign in ids_b, {"status": rb.status_code, "n": len(ids_b or [])})
    check("X2", f"A reads B's {name} by id -> 404", c.get(f"{API}{path}/{foreign}", headers=A).status_code == 404,
          c.get(f"{API}{path}/{foreign}", headers=A).status_code)
    check("X2", f"A reads own {name} by id -> 200", c.get(f"{API}{path}/{own}", headers=A).status_code == 200,
          c.get(f"{API}{path}/{own}", headers=A).status_code)
    for verb in ("PUT", "PATCH", "DELETE"):
        code = c.request(verb, f"{API}{path}/{foreign}", headers=A, json={"title": "x"}).status_code
        check("X5", f"A {verb} B's {name} -> no such route (405)", code == 405, code)

# Reference tampering on create: point at org B's rows.
tamper = [
    ("/students", {"first_name": "T", "last_name": "T", "school_id": S.SCHOOL_B}, "student in B's school"),
    ("/assessments", {"student_id": S.STUDENT_B, "title": "T", "assessment_type": "ela"}, "assessment on B's student"),
    ("/intervention-plans", {"student_id": S.STUDENT_B, "title": "T"}, "plan on B's student"),
    ("/intervention-plans", {"student_id": S.STUDENT_A, "assessment_id": S.ASSESSMENT_B, "title": "T"}, "plan citing B's assessment"),
    ("/assessment-results", {"assessment_id": S.ASSESSMENT_B, "summary": "T"}, "result on B's assessment"),
]
for path, body, label in tamper:
    r = c.post(API + path, headers=A, json=body)
    check("X3", f"A creates {label} -> 404", r.status_code == 404, r.status_code)

# Tenant-id tampering: body field and token claims.
for path, body in [("/students", {"first_name": "T", "last_name": "T"}),
                   ("/assessments", {"student_id": S.STUDENT_A, "title": "T", "assessment_type": "ela"})]:
    r = c.post(API + path, headers=A, json={**body, "organization_id": S.ORG_B})
    check("X4", f"A POST {path} with organization_id=B in body -> 422", r.status_code == 422, r.status_code)
    r = c.post(API + path, headers=A, json={**body, "created_by": S.USER_B})
    check("X4", f"A POST {path} with created_by=B user in body -> 422", r.status_code == 422, r.status_code)
spoof = bearer(token(S.AUTH_A, organization_id=S.ORG_B, user_id=S.USER_B, app_metadata={"organization_id": S.ORG_B}))
r = c.get(API + "/students", headers=spoof)
orgs = {x["organization_id"] for x in r.json()} if r.status_code == 200 else None
check("X4", "token claiming organization_id/user_id of B still scoped to A", r.status_code == 200 and orgs == {S.ORG_A},
      {"status": r.status_code, "orgs": sorted(orgs or [])})
check("X4", "spoofed-claims token cannot read B's student", c.get(f"{API}/students/{S.STUDENT_B}", headers=spoof).status_code == 404,
      c.get(f"{API}/students/{S.STUDENT_B}", headers=spoof).status_code)

# ---------------------------------------------------------------- R: direct PostgREST as authenticated A (RLS path)
RA = {"apikey": ENV["SUPABASE_ANON_KEY"], **bearer(rest_jwt(S.AUTH_A)), "Prefer": "return=representation"}
for tbl, foreign in (("students", S.STUDENT_B), ("assessments", S.ASSESSMENT_B),
                     ("intervention_plans", S.PLAN_B), ("assessment_results", S.RESULT_B)):
    rows = c.get(f"{REST}/{tbl}", headers=RA).json()
    check("R1", f"PostgREST as A lists {tbl}: no B rows", isinstance(rows, list) and rows
          and all(x["organization_id"] == S.ORG_A for x in rows), len(rows) if isinstance(rows, list) else rows)
    one = c.get(f"{REST}/{tbl}?id=eq.{foreign}", headers=RA).json()
    check("R2", f"PostgREST as A reads B's {tbl} by id -> empty", one == [], one)
    up = c.patch(f"{REST}/{tbl}?id=eq.{foreign}", headers=RA, json={"updated_at": "2000-01-01T00:00:00Z"})
    check("R3", f"PostgREST as A updates B's {tbl} -> 0 rows", up.status_code in (200, 204) and (up.status_code == 204 or up.json() == []),
          (up.status_code, up.text[:80]))
    de = c.delete(f"{REST}/{tbl}?id=eq.{foreign}", headers=RA)
    check("R4", f"PostgREST as A deletes B's {tbl} -> 0 rows", de.status_code in (200, 204) and (de.status_code == 204 or de.json() == []),
          (de.status_code, de.text[:80]))
ins = c.post(f"{REST}/students", headers=RA, json={
    "id": str(uuid.uuid4()), "organization_id": S.ORG_B, "first_name": "X", "last_name": "X", "created_by": S.USER_A})
check("R5", "PostgREST as A inserts a student into org B -> denied", ins.status_code in (401, 403), (ins.status_code, ins.json().get("code")))
mv = c.patch(f"{REST}/students?id=eq.{S.STUDENT_A}", headers=RA, json={"organization_id": S.ORG_B})
check("R6", "PostgREST as A moves own student into org B -> denied", mv.status_code >= 400, (mv.status_code, mv.text[:100]))

fp_after_attacks = b_fingerprint()
check("X6", "org B data byte-identical after all attacks", fp_before == fp_after_attacks,
      {"before": fp_before[0][:16], "after": fp_after_attacks[0][:16], "rows": fp_before[1]})

# ---------------------------------------------------------------- A: authorized operations
created = {}
r = c.post(API + "/students", headers=A, json={"first_name": "Pilot", "last_name": "Synthetic", "school_id": S.SCHOOL_A})
check("A1", "A creates a student -> 201", r.status_code == 201, (r.status_code, r.text[:160]))
if r.status_code == 201:
    created["students"] = r.json()["id"]
r = c.post(API + "/assessments", headers=A, json={"student_id": S.STUDENT_A, "title": "P0-01", "assessment_type": "ela"})
check("A1", "A creates an assessment -> 201", r.status_code == 201, (r.status_code, r.text[:160]))
if r.status_code == 201:
    created["assessments"] = r.json()["id"]
r = c.post(API + "/intervention-plans", headers=A, json={"student_id": S.STUDENT_A, "assessment_id": S.ASSESSMENT_A, "title": "P0-01"})
check("A1", "A creates an intervention plan -> 201", r.status_code == 201, (r.status_code, r.text[:160]))
if r.status_code == 201:
    created["intervention-plans"] = r.json()["id"]
r = c.post(API + "/assessment-results", headers=A, json={"assessment_id": S.ASSESSMENT_A, "score": 7, "max_score": 10})
check("A1", "A creates an assessment result -> 201", r.status_code == 201, (r.status_code, r.text[:160]))
if r.status_code == 201:
    created["assessment-results"] = r.json()["id"]

for name, rid in created.items():
    path = RES[name][0]
    check("A2", f"B cannot read A's new {name}", c.get(f"{API}{path}/{rid}", headers=B).status_code == 404,
          c.get(f"{API}{path}/{rid}", headers=B).status_code)

# ---------------------------------------------------------------- P: survive reload (full process restart)
subprocess.run([str(H / "stack.sh"), "down"], check=True)
subprocess.run([str(H / "stack.sh"), "up"], check=True)
c = httpx.Client(timeout=15, headers={"Connection": "close"})
A = bearer(token(S.AUTH_A))
for name in ("students", "assessments", "intervention-plans", "assessment-results"):
    path, own, _ = RES[name]
    rid = created.get(name)
    if rid is None:
        check("P1", f"A's new {name} survives app+PostgREST restart", False, "not created (see A1)")
        continue
    r = c.get(f"{API}{path}/{rid}", headers=A)
    check("P1", f"A's new {name} survives app+PostgREST restart", r.status_code == 200, r.status_code)
r = c.get(f"{API}/students/{S.STUDENT_A}", headers=A)
check("P2", "pre-existing seeded record readable after restart", r.status_code == 200, r.status_code)

# Guards against a silently shrinking harness: a check that stops running
# must not turn into a green run.
EXPECTED_CHECKS = 89
passed = sum(r["pass"] for r in results)
if len(results) != EXPECTED_CHECKS:
    print(f"expected {EXPECTED_CHECKS} checks, ran {len(results)}")
print(f"\n{passed}/{len(results)} checks passed")
(WORK / "e2e-results.json").write_text(json.dumps(results, indent=2))
sys.exit(0 if passed == len(results) == EXPECTED_CHECKS else 1)
