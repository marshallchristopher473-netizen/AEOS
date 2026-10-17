# Pilot Backend Contract — Teacher ELA Short-Response Pilot

| Field | Value |
| --- | --- |
| Inventory date | 2026-10-17 |
| Code basis | Candidate `claude/pr32-pter-reconcile-hcm5cf` @ `7a727920c6bf831a7dbc7951a5694bad2d77c23d` (PR #35, unmerged). Differences from `main` @ `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` are marked. |
| Deployment basis | **None verified.** See [`pilot-environment-map.md`](pilot-environment-map.md). Everything below describes code, not a running service. |
| Scope | Existing operations only. Gaps are listed separately in §6. No endpoint here is proposed or invented. |

---

## 1. Authentication (all non-health routes)

| Property | Value | Source |
| --- | --- | --- |
| Transport | `Authorization: Bearer <jwt>`. Missing → `401 Not authenticated`. | `app/core/auth.py` `get_current_user` |
| Issuer (`iss`) | `SUPABASE_JWT_ISSUER`, default `${SUPABASE_URL}/auth/v1`. Must match exactly. | `app/core/config.py` |
| Audience (`aud`) | `SUPABASE_JWT_AUDIENCE`, default `authenticated`. A missing `aud` is rejected explicitly. | `auth.py` |
| Signature | JWKS from `SUPABASE_JWKS_URL`, default `${SUPABASE_URL}/auth/v1/.well-known/jwks.json` (main: `/auth/v1/jwks`). Keys are selected by `kid`, with one forced refetch for an unknown `kid`. Algorithm is pinned by key type: RSA → RS256, EC P-256 → ES256. `oct`/HS256 keys are refused, and the token's `alg` header is never trusted. **main accepts RS256 only.** | `auth.py` `signing_algorithm` |
| Expiry | `exp` verified | `auth.py` |
| Subject | Non-empty `sub` required | `auth.py` |
| Auth errors | `401` invalid, unknown key or bad claims. `500` issuer/audience not configured. `503` JWKS unreachable or malformed. | `auth.py` |
| Issuer scope | Supabase Auth of the configured project only. **Base44 tokens are not accepted. No email matching.** | — |

## 2. Tenant and role derivation

| Step | Rule | Source |
| --- | --- | --- |
| Actor lookup | `users` row where `auth_user_id = sub` and `status = 'active'`. 0 rows → `403`. More than 1 → `403` (ambiguous). | `app/core/dependencies.py` `get_db_user` |
| Tenant | `organization_id` comes **only** from that row. The organization must have `status = 'active'`, else `403`. | `get_db_user` |
| Role | `users.role` ∈ `teacher`, `admin`, `support` (enum in 001). Never taken from the client. | `get_current_actor` |
| Write authority | `require_privileged_write` = teacher or admin, else `403` | `dependencies.py` |
| Read authority | Any active actor of any role in the organization | `get_current_actor` |
| Client-supplied tenant | Rejected: request models use `extra="forbid"`, and `insert_tenant_scoped_row` raises if a payload contains `organization_id` | `app/services/tenant_scope.py` |
| AI feedback extra gates | Feature flag `AEOS_AI_FEEDBACK_ENABLED`, else `503 feature_disabled`. Organization in `AEOS_AI_FEEDBACK_ORG_ALLOWLIST`, else `403 organization_not_enabled`. On generation, a complete config is also required, else `503 feature_misconfigured`. | `service.py` `ensure_available` |

## 3. Existing pilot operations

**Error envelope.** Core routes return FastAPI `{"detail": "<string>"}`. AI feedback routes return `{"detail": {"code", "message", ...}}` (`service.py` `api_error`). Validation failures return `422` with the Pydantic error list.

### 3.1 Assignment (closest existing entity: `assessment`)

There is no assignment or task entity. An `assessment` is one record per **student** (`student_id` is required). It carries no passage, prompt or rubric.

| Op | Method / path | Request | Response | Auth / role | Errors | Idempotency | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Create | `POST /assessments` | `student_id`, `title`, `assessment_type` (strings, min 1); `status` (string, default `draft`; free text); `notes?`. Extra keys forbidden. | `201 AssessmentResponse`: `id, organization_id, student_id, created_by, title, assessment_type, status, notes?, created_at?, updated_at?` | teacher, admin | `404 Student not found` (other tenant or missing), `403`, `422` | **None.** Each call inserts a row. | `app/api/assessments.py`, `assessment_service.py` |
| List | `GET /assessments` | — | `200 [AssessmentResponse]` for the actor's organization | any role | `401/403` | n/a | same |
| Get | `GET /assessments/{id}` | — | `200 AssessmentResponse` | any role | `404 Assessment not found` | n/a | same |

### 3.2 Rubrics and approved versions

| Op | Interface | Contract | Version binding | Source |
| --- | --- | --- | --- | --- |
| Rubric registry | **Server files**, not an endpoint or a table | `backend/app/services/ai_feedback/rubrics/<ID>.v<version>.json`. The only file is `RUB-CER3.v0.1.json`, status `PROPOSED-UNREVIEWED`, with criteria C1–C3 (levels `0/1/2`, `IE` defined). | `sha256` of canonical JSON. A rubric is usable only if `"<id>@<version>:<sha256>"` is in `AEOS_AI_FEEDBACK_APPROVED_RUBRICS`. That list is **empty**, so every draft returns `422 rubric_not_approved`. Editing a file changes its hash and revokes approval. | `services/ai_feedback/rubrics.py` |
| Selection | A field on draft create (§3.4) | Client sends `rubric_id` and `rubric_version` only, never rubric content | Unknown → `422 rubric_not_found`. Unpinned → `422 rubric_not_approved`. | `service.py` `create_draft` |
| List / read rubrics | **None** | — | — | — |

### 3.3 Student responses

Responses are not a stored entity of their own. `response_text` (1–4000 chars, not blank) and an optional `source_text` (≤ 6000) are sent **inline** with each draft request. They are stored on `ai_feedback_requests` with `data_classification = 'synthetic'`, enforced by a Pydantic `Literal` and a DB `CHECK`. They are returned in `AiFeedbackDraftResponse.response_text`. There is no submit, list or get operation for responses.

### 3.4 Evaluation drafts (AI feedback drafts)

The AI drafts **feedback text with evidence quotes**. It never produces a score. Rubric values `0/1/2/IE` are not emitted, and scoring language is rejected by `validation.py`.

| Op | Method / path | Request | Response | Auth / role | Errors | Idempotency | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Create | `POST /ai-feedback/drafts` | Header `Idempotency-Key: <UUID>` (required). Body: `assessment_id`, `rubric_id`, `rubric_version`, `response_text`, `source_text?`, `data_classification: "synthetic"`. Extra keys forbidden. | `201` new draft, or `200` replay: `AiFeedbackDraftResponse` (below) | teacher, admin + flag + allowlist | `400 idempotency_key_required`; `404 Assessment not found`; `422 rubric_not_found / rubric_not_approved`; `409 idempotency_key_reused / request_in_progress`; `429` user/org rate or budget limits (`user_rate_limited`, `org_rate_limited`, `user_budget_exceeded`, `org_budget_exceeded`); `502 invalid_model_output` (with `draft_id`, `reason`); `502/503` provider codes; `500 draft_not_saved`; `503 feature_disabled / feature_misconfigured`; `403 organization_not_enabled` | Key unique per `(organization_id, created_by, request_key)`. Same key and same canonical input hash → replay without a second provider call. Same key with a different input → `409`. | `app/api/ai_feedback.py`, `services/ai_feedback/service.py`, migration 006 |
| List | `GET /ai-feedback/drafts?assessment_id=` | Query `assessment_id` (required) | `200 [AiFeedbackDraftResponse]` | any role + flag + allowlist | `404 Assessment not found`, `503`, `403` | n/a | same |
| Get | `GET /ai-feedback/drafts/{draft_id}` | — | `200 AiFeedbackDraftResponse` | any role + flag + allowlist | `404 Draft not found` | n/a | same |

`AiFeedbackDraftResponse` (`app/models/ai_feedback.py`, **reconstructed module, pending review**) has these fields: `id, organization_id, request_id, assessment_id, student_id, requested_by, status, feedback?{overall_abstention?, criteria[{criterion_id, criterion_name, outcome: feedback|abstain, strength?, next_step?, evidence[{start,end,quote}], abstention_reason?}]}, draft_text?, review_flags[], error_code?, response_text, provider, model_id, response_model_id?, prompt_version, rubric_id, rubric_version, rubric_sha256, input_tokens?, output_tokens?, actual_cost_microusd, data_classification, decisions[], current_decision?, created_at?`.

**Version binding per draft.** Each draft stores `rubric_id`, `rubric_version`, `rubric_sha256`, `prompt_version` (`aeos-ela-feedback-draft-v1`), `provider`, `model_id` (the configured model, checked against the provider's live model list) and `response_model_id`. Rows are append-only (UPDATE-rejecting triggers in 006).

### 3.5 Teacher decisions

| Op | Method / path | Request | Response | Auth / role | Errors | Idempotency | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Record | `POST /ai-feedback/drafts/{draft_id}/decisions` | Header `Idempotency-Key: <UUID>`. Body: `decision: accepted\|revised\|rejected`; `approved_text` (required for accepted/revised, forbidden for rejected, ≤ 6000); `review_flags_acknowledged` (bool); `teacher_confirmed: true` (literal). | `201`, or `200` replay: the draft with `decisions[]` and `current_decision` | teacher, admin + flag + allowlist | `404 Draft not found`; `409 draft_not_reviewable / decision_key_reused`; `422 accept_requires_ready_draft / accepted_text_mismatch / revision_unchanged / review_flags_not_acknowledged`; `500 decision_not_saved` | Key unique per `(organization_id, decided_by, decision_key)` with a payload hash. Append-only: the latest row is the current decision. | `ai_feedback.py`, `service.py` `record_decision`, 006 |

**Accept** requires `approved_text` to equal `draft_text` exactly. **Revise** requires changed text. The AI draft row is never overwritten. Any active teacher or admin of the organization may decide on any draft in that organization; the code does not restrict decisions to the requesting teacher (§6, G9).

### 3.6 Status

| Entity | Values | Who sets it |
| --- | --- | --- |
| Draft `status` | `ready`, `abstained`, `rejected_output`, `provider_error`, `provider_refused` (enum, 006) | Server only. Reviewable states are `ready` and `abstained`. |
| Decision | `accepted`, `revised`, `rejected` (enum, 006) | Teacher |
| Assessment `status` | Free-text string, default `draft` | Client (create only, no update route) |
| Assessment result `status` | `draft`, `submitted`, `in_review`, `complete` (candidate). `main`: free text. | Client (create only) |

There is no status-transition or workflow endpoint.

### 3.7 Evidence

Evidence is held inside the draft: `feedback.criteria[].evidence[{start, end, quote}]`. The server locates each model quote verbatim in `response_text` (≥ 8 chars). A quote it can't find is removed, and the criterion becomes `abstain` / `evidence_not_verified` with the server flag `unverified_evidence_removed` (`services/ai_feedback/validation.py`). There is no separate evidence endpoint or table.

### 3.8 Audit

| Interface | Contract | Source |
| --- | --- | --- |
| DB triggers → `public.audit_logs` | `AFTER INSERT` on drafts (`action = 'ai_feedback.draft.<status>'`) and on decisions. Metadata holds ids, status, provider, model, prompt and rubric versions, flag count and cost. **No student text.** If the audit insert fails, the save fails. | migration 006, `SECURITY DEFINER` functions |
| Read | **No API.** RLS policy `audit_logs_select` allows `authenticated` to read their own organization's rows directly via PostgREST (002). | 002 |
| Core routes | Assessment, result, student and plan writes are **not** audited | — |

### 3.9 Assessment results (scores, existing but not AI-linked)

`POST /assessment-results` (teacher, admin), `GET /assessment-results[?assessment_id=]` (filter added at candidate), `GET /assessment-results/{id}`. Body: `assessment_id`, `score?` (0–9999.99), `max_score?` (0.01–9999.99), `summary?`, `status`. `student_id` is derived from the assessment. No idempotency. A teacher's rubric value can only be stored here as a number. Nothing links it to a draft, decision or criterion. Source: `app/api/assessment_results.py`, `assessment_result_service.py`.

## 4. Database access model

| Question | Answer |
| --- | --- |
| Client used by every business route | `get_supabase_admin_client()`, a Supabase client built with `SUPABASE_SERVICE_ROLE_KEY` (`app/services/supabase_service.py`) |
| Caller-scoped RLS? | **No.** The user's JWT is never forwarded to PostgREST. |
| Restricted DB role? | **No** |
| Privileged access? | **Yes.** `service_role` has `BYPASSRLS`. `FORCE ROW LEVEL SECURITY` does not apply to a BYPASSRLS role, so RLS policies 002–006 do **not** protect backend queries. |
| Exception | `/health` uses the anon-key client to `SELECT id FROM organizations LIMIT 1` |
| What still binds the service role | Migration 006 `BEFORE INSERT` integrity triggers (same tenant, active teacher/admin, reviewable draft), append-only triggers, CHECK constraints, and `aeos_reserve_ai_feedback_request` (EXECUTE granted to `service_role` only) for rate and budget limits |

### Backend authorization boundary that must be tested (on a real database)

Because RLS is bypassed, isolation depends on application code:

1. `get_db_user` / `get_current_actor` derive the organization and role from the `users` and `organizations` rows. They never use a claim or the request body.
2. Every query goes through `tenant_scope.py`, which adds `.eq("organization_id", actor.organization_id)`. A foreign id therefore returns `404`, not another tenant's row.
3. Related-row checks (`assert_related_row_in_tenant`) run before writes.
4. On AI feedback: `ensure_available` (flag + allowlist) and `require_privileged_write`.

Existing route tests for these (`test_ai_feedback.py::test_foreign_draft_cannot_be_read_listed_or_decided`, `::test_foreign_assessment_is_not_found_and_never_sent_to_the_provider`) run against an **in-memory fake** (`tests/fakes.py`). They don't use supabase-py and PostgREST against migrated Postgres. The DB tests (`test_ai_feedback_rls.py`) prove RLS for client roles and the trigger guards. They do not prove the HTTP routes. **Required test:** for each route in §3, two tenants on the hosted pilot DB with migrations 001–006 applied, the service-role client, and cross-tenant id substitution must return `404` with no row returned.

## 5. Identity separation

The `users.auth_user_id` ↔ Supabase JWT `sub` link is the only identity link. Base44 identities have no mapping, so a Base44 session cannot call this API. Any future bridge must be an explicit, audited link created by an admin. It must not match on email and must not trust a Base44 JWT.

## 6. Gaps (proposed: not implemented, no endpoint invented)

| # | Gap | Effect on the pilot |
| --- | --- | --- |
| G1 | No assignment/task entity holding passage, prompt and rubric for a class | Each draft resends the passage and response text |
| G2 | No rubric list/read API. Approval is an env-var hash pin, and the pin list is empty. | Drafting is disabled until a human approves RUB-CER3 (or a successor) |
| G3 | No stored student-response entity | No response history apart from drafts |
| G4 | Teacher rubric value (`0/1/2/IE`) per criterion is not captured or linked to the draft. Decisions are per draft, not per criterion (P-TER-01 D1/D2 open). | The pilot cannot measure agreement per criterion through the API |
| G5 | No audit read API. Core routes are not audited. | Evidence export needs direct DB access |
| G6 | No idempotency on core create routes | Retries duplicate rows |
| G7 | Reconstructed `app/models/ai_feedback.py` not human-reviewed | Contract fields above may differ from the original intent |
| G8 | Hosted DB lacks migrations 001–006 (see environment map §3) | Routes in §3.4–3.5 cannot run against AEOS-MVP as reported |
| G9 | Any teacher/admin in the organization can read, and decide on, any draft. Decisions are not restricted to the requesting teacher or an admin. `support` can read draft text. | Intra-tenant authorization is broader than "teacher control" |

## 7. Launch route recommendation

| Option | Completion | Validation | Security | Verdict |
| --- | --- | --- | --- | --- |
| **Next.js `frontend/` → `/api` rewrite (`AEOS_API_URL`) → FastAPI candidate → Supabase (one project built from migrations 001–006)** | Code exists (`AiFeedbackPanel.tsx`, `lib/aiFeedback.ts`) | Same server-side flow the tests cover | Single issuer, service-role boundary as above | **Recommended** |
| Base44 UI → `AEOS_API` | Integration disabled. No identity bridge. | Synthetic demo only | Would need a Base44↔Supabase identity design | Optional, later |

**Smallest route:** use the existing Next.js pages. The pilot teacher signs in with Supabase Auth on the pilot project. The browser calls same-origin `/api/*`, which Next rewrites to the backend. Note: the frontend reads the token from `localStorage['aeos_access_token']` and has **no sign-in screen**. That is a launch gap for any non-developer user (G10).

## 8. Next single bounded security repair

**Restrict AI-feedback decisions to the requesting teacher or an organization admin (G9).**

| Field | Value |
| --- | --- |
| Change | In `AiFeedbackService.record_decision`, reject (`403`) unless `actor.user_id == request.created_by` or `actor.role == 'admin'`. Add a forward-only migration `007` that applies the same rule in `aeos_ai_feedback_decision_integrity`. |
| Tests | A second teacher in the same organization gets `403` (route test) and the trigger rejects the insert (Postgres test). Admin is allowed. The original teacher is allowed. Replay is unchanged. |
| Out of scope | Read restrictions, `support` visibility, new endpoints |
| Done when | Both tests fail on 7a72792, pass after the change, and the full backend suite stays green in CI on the exact head |

Run this only after the owner accepts this contract. Nothing was changed in this task.

## 9. Source references (@ 7a72792 unless noted)

`backend/app/main.py`; `app/core/auth.py`; `app/core/config.py`; `app/core/dependencies.py`; `app/core/ai_feedback_settings.py`; `app/api/ai_feedback.py`; `app/api/assessments.py`; `app/api/assessment_results.py`; `app/models/schemas.py`; `app/models/ai_feedback.py` (reconstructed); `app/services/supabase_service.py`; `app/services/tenant_scope.py`; `app/services/ai_feedback/{service,rubrics,validation,prompt}.py`; `app/services/ai_feedback/rubrics/RUB-CER3.v0.1.json`; `supabase/migrations/001`–`006`; `tests/test_ai_feedback.py`; `tests/test_ai_feedback_rls.py`; `tests/fakes.py`; `frontend/next.config.mjs`; `frontend/src/lib/api.ts`.
