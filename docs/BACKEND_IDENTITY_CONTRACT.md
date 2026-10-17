# AEOS backend identity and API contract

**Version:** 0.1 · **Derived from:** `main` @ `b9c68aa` · **Owner:** AEOS backend (`backend/`)

This is the contract any AEOS client — the Next.js app in `frontend/`, the
Base44 prototype, or a future module — must follow to call the AEOS API. It is
written from the code, not from intent. The endpoint table in §5 is checked
against the running FastAPI app by `backend/tests/test_contract_document.py`;
if a route or its access level changes without this file changing, CI fails.

## 0. Evidence level — read this first

| Claim | Level | Evidence |
| --- | --- | --- |
| Token verification, actor resolution, tenant scoping and RLS behave as described | **Internal test** | 170 backend tests and the M01–M18 mutation contract (`docs/P0_MUTATION_VERIFICATION.md`), run in CI against PostgreSQL 16 |
| P0 security boundary is closed | **Not claimed** | Independent P0 verification has not signed off |
| Works against a real Supabase project | **Not verified** | No project is provisioned; all Supabase values below are templates |
| A deployed API exists | **No** | There is no base URL. See §8 gate G1 |
| Safe for real student data | **No** | Blocked by §8 gates. Use synthetic data only |

## 1. Topology

```
Browser client ──(1) sign in──▶ Supabase Auth
      │                              │
      │◀──── Supabase access token ──┘
      │
      └──(2) Authorization: Bearer <token>──▶ AEOS FastAPI ──service role──▶ Supabase Postgres (RLS forced)
```

- The **identity provider** is Supabase Auth. The AEOS API never issues tokens.
- The **authorization authority** is the AEOS API plus Postgres RLS. A client
  never decides tenant or role.
- There is **no token exchange**. A token issued by any other system (including
  a Base44 app session token) fails issuer, audience and signature checks and is
  rejected with 401. The only supported bridge is: the client signs the person
  in to Supabase Auth directly and sends *that* access token.

## 2. Token contract

Source: `backend/app/core/auth.py`, `backend/app/core/config.py`.

| Property | Required value | On violation |
| --- | --- | --- |
| Transport | `Authorization: Bearer <access_token>` | 401 `Not authenticated` |
| Signature algorithm | **RS256 only** | 401 |
| Header `kid` | present, non-empty, matches a key in the JWKS | 401 (no fallback to another key) |
| `iss` | exactly `SUPABASE_JWT_ISSUER` (default `${SUPABASE_URL}/auth/v1`) | 401 |
| `aud` | must be present and include `SUPABASE_JWT_AUDIENCE` (default `authenticated`) | 401 — a *missing* `aud` is also rejected |
| `exp` | in the future; no leeway | 401 |
| `sub` | non-empty string (the Supabase `auth.users.id`) | 401 |
| JWKS location | `SUPABASE_JWKS_URL` (default `${SUPABASE_URL}/auth/v1/jwks`) | 503 if unreachable or malformed |

**Claims that are never trusted for authorization:** `organization_id`,
`user_id`, `role` (in a Supabase token this is the Postgres role
`authenticated`, not an AEOS role), `email`, `app_metadata`, `user_metadata`.
Adding them to a token changes nothing (mutations M03, M04).

## 3. Identity binding

Source: `backend/app/core/dependencies.py`.

On every request, after the token verifies:

1. Look up `public.users` where `auth_user_id = sub` **and** `status = 'active'`.
2. Zero rows → **403** `Authenticated identity has no active AEOS user`.
3. More than one row → **403** `…ambiguous AEOS user`. (The schema allows one
   Supabase identity in several organizations; the API refuses to guess.)
4. The user's organization must have `status = 'active'` → otherwise **403**.
5. The request's `user_id`, `organization_id` and `role` come **only** from
   that database row.

**Email is never used to match an identity.**

**Provisioning:** there is no sign-up or invite endpoint. An operator must
insert the `organizations` and `users` rows, setting `users.auth_user_id` to
the person's Supabase `auth.users.id`. A person who signs in to Supabase without
that row gets 403, not access.

## 4. Authorization

| Rule | Behavior |
| --- | --- |
| Roles | `teacher`, `admin`, `support` (`user_role` enum) |
| Read (GET) | any active user in an active organization |
| Create (POST) | `teacher` or `admin`; `support` → 403 |
| Update / delete | **not exposed by the API.** RLS defines them for direct database access: update = teacher/admin, delete = admin only |
| Tenant | `organization_id` is always set server-side. Request bodies reject unknown fields, so sending `organization_id` or `created_by` → 422 |
| Linked IDs | every referenced `student_id`, `school_id` or `assessment_id` must belong to the caller's tenant, otherwise 404 — indistinguishable from "does not exist". An intervention plan's `assessment_id` must also belong to the same student |
| Cross-tenant reads | 404, never 403, so a caller cannot probe for other tenants' IDs |

## 5. Endpoints

Access levels: `public` = no token; `member` = any active user;
`teacher_or_admin` = privileged write.

<!-- contract-routes:start -->
| Method | Path | Access |
| --- | --- | --- |
| GET | /health | public |
| GET | /students | member |
| GET | /students/{student_id} | member |
| POST | /students | teacher_or_admin |
| GET | /assessments | member |
| GET | /assessments/{assessment_id} | member |
| POST | /assessments | teacher_or_admin |
| GET | /assessment-results | member |
| GET | /assessment-results/{assessment_result_id} | member |
| POST | /assessment-results | teacher_or_admin |
| GET | /intervention-plans | member |
| GET | /intervention-plans/{plan_id} | member |
| POST | /intervention-plans | teacher_or_admin |
<!-- contract-routes:end -->

FastAPI also serves `/docs`, `/redoc` and `/openapi.json` without
authentication. They expose the API schema only, never data, and are excluded
from the table above.

**Request bodies** (all reject unknown fields; full schemas at `/openapi.json`):

| Endpoint | Required | Optional (default) |
| --- | --- | --- |
| `POST /students` | `first_name`, `last_name` | `school_id`, `student_number`, `grade_level`, `iep_status` (false), `birth_date` |
| `POST /assessments` | `student_id`, `title`, `assessment_type` | `status` ("draft"), `notes` |
| `POST /assessment-results` | `assessment_id` | `score`, `max_score`, `summary`, `status` ("draft") |
| `POST /intervention-plans` | `student_id`, `title` | `assessment_id`, `status` ("draft"), `summary`, `priority` ("medium") |

`created_by`, `organization_id` and (for results) `student_id` are always
filled in by the server.

**Client rule:** a client may enable an operation only if it appears in this
table. Any client adapter method without a matching row here must stay
disabled — do not point it at a guessed path.

## 6. Error semantics

| Status | Meaning |
| --- | --- |
| 401 | Missing, malformed, expired, wrongly-signed, wrong-issuer or wrong-audience token |
| 403 | Valid token but no single active AEOS user, organization suspended, or role not allowed |
| 404 | Not found **or** belongs to another tenant (deliberately indistinguishable) |
| 422 | Request body failed validation, including forbidden authority fields |
| 500 | Server misconfigured (issuer/audience/JWKS URL not set) |
| 503 | JWKS endpoint unreachable or returned an invalid key set |

## 7. Revocation, replay and key rotation

| Concern | Current behavior |
| --- | --- |
| Remove a person's access | **Immediate.** Set `users.status = 'disabled'`; the next request is 403 |
| Remove an organization's access | **Immediate.** Set `organizations.status = 'suspended'`; enforced in the API and in RLS |
| Revoke an issued access token | **Not supported.** A token stays cryptographically valid until `exp`, even after Supabase sign-out. Exposure is bounded by the project's access-token lifetime. The two status switches above are the containment controls |
| Replay / nonce | **None.** Standard bearer-token model; relies on TLS and short expiry |
| Key rotation (new `kid`) | Supported: an unknown `kid` triggers one JWKS refetch |
| Key revocation (removed `kid`) | **Gap.** The JWKS is cached in-process with no expiry. A key removed from the JWKS stays trusted until the API process restarts. Operational rule until fixed: **restart the API after revoking a Supabase signing key** |

## 8. Gates before any browser client can call this API

Ranked by what blocks first. None of these are closed.

| # | Gate | Why it blocks | Smallest closing action |
| --- | --- | --- | --- |
| G1 | No deployment, no base URL | Nothing to call | Deploy the API to a staging host with synthetic data; record the URL here |
| G2 | No Supabase project | No issuer, JWKS or users | Create a staging project; set the four `SUPABASE_*` values server-side only |
| G3 | Signing-algorithm mismatch risk | The API accepts **RS256 only**. Supabase also supports Elliptic Curve (ES256) keys, and legacy projects use a shared HS256 secret that publishes no JWKS keys. Either one yields 401 on every request | Configure the project with an RSA signing key, **or** extend `auth.py` to ES256 with tests and a mutation-contract update |
| G4 | JWKS path unverified | Supabase documents both `/auth/v1/jwks` and `/auth/v1/.well-known/jwks.json`; the default here has not been tested against a live project | `curl` the project's JWKS once; set `SUPABASE_JWKS_URL` explicitly to the path that returns keys |
| G5 | No CORS policy | The app adds no CORS middleware, so browsers block calls from any other origin (`*.base44.app`, a Vercel domain) | Add `CORSMiddleware` with an explicit origin allowlist from configuration — never `*` |
| G6 | No audit writes | `audit_logs` exists with RLS, but no route writes to it. MVP acceptance criteria §2, §3, §7 require audit | Write an audit row on every create and every student read, in the same request |
| G7 | No provisioning path | Users can only be added by direct SQL | Acceptable for a ≤3-teacher synthetic pilot; document the SQL runbook |

Not gates for a synthetic-data pilot, but known and open: no update or delete
endpoints, no AI recommendation endpoint, and the Next.js client reads its
token from `localStorage` with no login flow writing it.

## 9. Verify this contract yourself

```bash
cd backend
pip install -r requirements-dev.txt

# Contract-vs-code drift check (no database needed)
python -m pytest tests/test_contract_document.py -q

# Full suite including real-PostgreSQL RLS denial tests
export AEOS_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
AEOS_REQUIRE_RLS_TESTS=1 python -m pytest tests/ -q
```
