# AI feedback drafting (teacher review)

| Field | Value |
| --- | --- |
| Status | **Prototype on a draft branch.** Feature flag OFF by default. Not merged, not deployed, not launched. |
| Data | **Synthetic ELA short responses only.** The API refuses any other `data_classification`. |
| Base | Stacked on the release candidate `p0/security-release-candidate-20261010` (draft PR #28) @ `3816773`. |
| Claims | None about feedback accuracy, quality, time saved or outcomes. No evaluation has been run. |

## The workflow

```
synthetic response ─▶ POST /ai-feedback/drafts ─▶ immutable AI draft (or abstention / recorded failure)
                                                          │
          teacher reads criteria, evidence, flags ◀───────┘
                                                          │
 explicit button press ─▶ POST /ai-feedback/drafts/{id}/decisions ─▶ accepted | revised | rejected
                                                          │            (append-only; latest row is current)
                                                          ▼
                                     teacher-approved text lives ONLY in ai_feedback_decisions
```

Nothing writes to `assessment_results`, intervention plans, a gradebook, an IEP, or any outbound message.

## What was inspected first, and the decision

| Existing piece | Finding | Used? |
| --- | --- | --- |
| `ai_recommendations` (migration 001) | Unused by any service or route. One free-text column, a `confidence_score`, and a status the teacher would change by `UPDATE`. Its 003/004 policies let teachers update it. | **No.** Recording a decision by updating the AI row would let the AI text be overwritten by, and become indistinguishable from, teacher-approved text. It also lacks criterion links, evidence spans, versions and an idempotency key. |
| `assessment_results` review semantics | Every save is a new row; nothing is edited in place; latest row is current. | **Matched.** Decisions follow the same append-only rule. |
| `tenant_scope.py`, `require_privileged_write`, `get_current_actor` | Server-derived organization, role and author; 404 for foreign rows. | **Reused** for every query and write. |
| Supabase service-role client | Server-only; bypasses RLS, so app-layer scoping is mandatory. | **Reused**, plus database-level controls below. |
| Draft PR #30 synthetic harness | Original passage, provisional rubric RUB-CER3 (status `PROPOSED-UNREVIEWED`), 10 authored responses incl. two injection attempts. | **Copied** (passage, rubric, four responses) with provenance; rubric status left unreviewed. |

**Narrow versioned change:** forward-only migration `006_ai_feedback_drafts.sql` adds three tables and edits none of 001–005.

| Table | Written | Purpose |
| --- | --- | --- |
| `ai_feedback_requests` | Before the provider call, by an atomic reservation function | Idempotency key, synthetic input snapshot, rubric/prompt/model versions, worst-case cost reservation |
| `ai_feedback_drafts` | Once per request, after the call | Validated output or abstention, review flags, token usage and actual cost. Failures are recorded too (`rejected_output`, `provider_error`, `provider_refused`). |
| `ai_feedback_decisions` | Only by an explicit teacher request | `accepted` / `revised` / `rejected`, approved text, flag acknowledgement, `teacher_confirmed` (CHECK = true) |

Database guarantees (all executed against PostgreSQL 16 in tests): RLS enabled and forced, with SELECT limited to **the requesting teacher and org admins** (migration 007; 006 allowed every member) and **no client write policy**; a decision must be recorded by **the teacher who requested the draft** (007 trigger check); `UPDATE` refused for **every role** by trigger; audit rows written by `AFTER INSERT` triggers **in the same transaction** (a save fails if its audit row fails); integrity triggers keep requests/decisions inside one organization and restrict them to active teachers/admins; composite foreign keys stop a draft or decision pointing at another organization's row; `DELETE` is left to the service role for offboarding/retention only.

## Files

| Path | Role |
| --- | --- |
| `backend/supabase/migrations/006_ai_feedback_drafts.sql` | Tables, RLS, append-only + audit + integrity triggers, `aeos_reserve_ai_feedback_request` |
| `backend/supabase/migrations/007_ai_feedback_draft_ownership.sql` | Draft ownership: requester-or-admin SELECT policies, requester-only decisions ([repair record](DRAFT_OWNERSHIP_REPAIR_2026_10_17.md)) |
| `backend/app/core/ai_feedback_settings.py` | Server-only configuration and feature flag; fails closed |
| `backend/app/services/ai_feedback/rubrics.py`, `rubrics/RUB-CER3.v0.1.json` | Rubric registry; usable only when its content hash is pinned by an approver |
| `backend/app/services/ai_feedback/prompt.py` | Server-owned system instructions, `PROMPT_VERSION`, untrusted-data block, injection heuristic |
| `backend/app/services/ai_feedback/provider.py` | Provider adapter (official `anthropic` SDK 1.8.0): explicit key and endpoint, live model check, bounded timeout/retries, sanitized error codes |
| `backend/app/services/ai_feedback/validation.py` | Strict output validation, verbatim evidence location, prohibited-inference/scoring scan |
| `backend/app/services/ai_feedback/service.py` | Orchestration: gates, idempotency, reservation, persistence, decisions |
| `backend/app/models/ai_feedback.py` | Request/response and provider-output contracts |
| `backend/app/api/ai_feedback.py` | Four routes under `/ai-feedback` |
| `frontend/src/lib/aiFeedback.ts`, `frontend/src/app/assessments/[id]/AiFeedbackPanel.tsx` | Browser client (talks only to the AEOS backend) and the review panel |
| `backend/tests/test_ai_feedback*.py`, `frontend/tests/ai-feedback-api.test.mjs` | Tests (deterministic fixtures, labeled) |
| `backend/tests/ai_feedback_fixture_server.py` | Loopback-only browser fixture with a deterministic provider |
| `backend/tests/ai_feedback_provider_smoke.py` | Manual genuine-provider smoke check (spends money; never in CI) |
| `docs/evidence/ai-feedback/` | Mutation and browser evidence from this change |

## Safety controls and where each is tested

| Requirement | Implementation | Test (all deterministic fixtures) |
| --- | --- | --- |
| Server-mediated, no browser provider call | Only the backend constructs the SDK client; the browser posts to `/api/ai-feedback/*` | `test_frontend_never_calls_a_provider_or_reads_provider_config`, frontend contract tests |
| No service-role exposure | Unchanged server-only client; frontend scanned | existing `test_service_role_key_is_not_referenced_by_frontend_source` + the scan above |
| Configurable model, never stale | `AEOS_AI_FEEDBACK_MODEL` has no default; `models.retrieve` must return it with `structured_outputs.supported` and enough `max_tokens`; cached 10 min (failures 30 s) | `test_model_check_fails_closed[*]`, `test_unavailable_model_fails_before_any_reservation_or_call` |
| Secret handling | Key read from env, `repr=False`, passed explicitly; ambient `ANTHROPIC_*` env ignored; base URL pinned and must be `https` | `test_real_adapter_uses_only_explicit_credentials_and_endpoint`, `test_settings_never_expose_the_api_key` |
| Server-owned instructions | Constant `SYSTEM_INSTRUCTIONS`, hash pinned to `PROMPT_VERSION` | `test_system_instructions_are_pinned_to_the_prompt_version`, `extra="forbid"` rejects `system_prompt`/`model_id` fields |
| Untrusted student/source text | JSON-encoded inside `<untrusted_input_json>` with `<`, `>`, `&` escaped; instructions say it is data; heuristic adds `possible_embedded_instructions` | `test_injection_text_stays_data_and_is_flagged[R05,R10]`, `test_student_text_cannot_close_the_data_block_or_open_a_rubric_section`, `test_provider_that_obeys_an_injection_is_contained_by_validation` |
| Strict request schema + size limits | Response ≤ 4,000 chars, source ≤ 6,000; `data_classification` must be `"synthetic"`; unknown fields rejected; DB CHECKs repeat the limits | `test_request_contract_rejects_oversize_unsafe_or_authority_fields[*]`, `test_request_shape_constraints[*]` |
| Strict output schema | Provider structured-output mode **and** strict Pydantic validation (no extra fields, exact criterion coverage, length/count limits) | `test_malformed_or_out_of_contract_output_is_rejected_and_recorded[14 cases]` |
| Actual evidence spans or abstention | Model returns quotes only; server locates each verbatim (≥ 8 chars) and computes offsets; any unverifiable quote turns that criterion into `evidence_not_verified` and flags the draft | `test_invented_evidence_*`, `test_near_miss_and_trivial_quotes_*[4]`, `test_all_evidence_invented_*` |
| No ADHD / disability / eligibility / intelligence / reading age / mastery / standards inference, no scoring | No such output field exists; instructions forbid it; model-authored text is scanned and the whole output rejected on a match | `test_prohibited_inferences_and_scoring_reject_the_whole_output[11]`, `test_prohibited_words_inside_verified_student_quotes_do_not_reject` |
| Per-user/org rate limits and budgets | `aeos_reserve_ai_feedback_request` checks and inserts under a per-organization advisory lock; in-flight requests count at worst-case reservation, completed ones at actual cost | API: `test_org_cost_limit_*`, `test_user_cost_limit_counts_actual_spend`, `test_user_hourly_rate_limit`; DB: `test_concurrent_reservations_cannot_jointly_overspend`, `test_budget_counts_reservations_until_actual_cost_is_recorded` |
| Timeout, bounded retry | SDK `timeout` (default 30 s, ceiling 120 s) and `max_retries` (default 2, ceiling 3; SDK retries only connection errors, 408, 409, 429, 5xx) | `test_real_adapter_uses_only_explicit_credentials_and_endpoint` |
| Sanitized errors | Fixed `{code, message}`; provider messages never returned or logged (class + request id only) | `test_provider_errors_map_to_fixed_codes_without_echoing_content[10]`, `test_provider_outage_is_sanitized_recorded_and_not_billed` |
| Refusal / truncation | `stop_reason` `refusal` → `provider_refused`; `max_tokens` → `rejected_output/truncated_output` | `test_refusal_and_truncation_are_not_shown_as_drafts[2]` |
| Duplicate requests and saves | Required `Idempotency-Key` (UUID); same key + payload replays the stored outcome without calling the provider (even while it is down); different payload → 409; unique constraints in the DB | `test_duplicate_draft_request_replays_*`, `test_replay_returns_the_stored_draft_even_while_the_provider_is_down`, `test_duplicate_decision_save_is_bounded_to_one_row`, DB `test_duplicate_key_returns_the_original_request` |
| Foreign IDs | Every lookup scoped by server-derived organization → 404; DB integrity triggers + composite FKs | `test_foreign_assessment_*`, `test_foreign_draft_cannot_be_read_listed_or_decided`, DB `test_requests_must_stay_inside_one_organization_*` |
| Draft ownership inside one organization | Only the requesting teacher and org admins read a draft (others get the same 404 as a missing draft); only the requesting teacher decides it (admin → 403 `not_draft_owner`); same rule in RLS and the decision trigger (007) | `test_peer_teacher_cannot_read_list_or_decide_another_teachers_draft`, `test_admin_can_read_but_not_decide_another_teachers_draft`, `test_each_teacher_sees_only_their_own_drafts_and_admin_sees_all`, DB `test_only_the_requester_and_org_admins_read_a_feedback_chain[3]`, `test_only_the_requesting_teacher_can_decide_a_draft` + negative control; mutations M21a–g |
| Unauthenticated access | Existing bearer dependency on all four routes | `test_every_business_route_requires_authentication` (+4 routes) |
| Human approval required | Draft never creates a decision; decisions need `teacher_confirmed: true`, teacher/admin role, exact text for `accepted`, changed text for `revised`, flag acknowledgement when flagged; abstentions cannot be accepted | `test_draft_alone_never_creates_a_decision_*`, `test_decision_requires_an_explicit_well_formed_teacher_action[6]`, `test_accepting_altered_text_*`, `test_flagged_draft_requires_flag_acknowledgement_*`, `test_support_role_cannot_request_or_decide`, DB `test_decisions_require_reviewable_drafts_*` |
| AI draft separate from teacher text | Draft row immutable; decision rows separate; DB refuses UPDATE for all roles | `test_teacher_accept_persists_separately_*`, DB `test_owner_cannot_rewrite_the_ai_draft_into_teacher_text` + negative control |
| Audit accountability | Same-transaction audit triggers; metadata carries versions and ids, never student text | DB `test_draft_and_decision_saves_write_audit_rows_without_student_text`, `test_a_save_fails_when_its_audit_row_cannot_be_written` |

## Contract examples

Captured from the loopback fixture server (production routes, schemas and validator; deterministic provider). IDs are synthetic.

**Request a draft**

```http
POST /ai-feedback/drafts
Authorization: Bearer <session>
Idempotency-Key: 11111111-2222-4333-8444-555555555555
Content-Type: application/json

{"assessment_id": "55555555-5555-4555-8555-555555555555",
 "rubric_id": "RUB-CER3", "rubric_version": "0.1",
 "response_text": "Cool roofs can help a building use less electricity because the coating reflects sunlight.",
 "data_classification": "synthetic"}
```

`201 Created` (a replay with the same key and body returns `200` and the same draft):

```json
{
  "id": "dfa8e18a-8dfc-460b-af8a-ba0ffe70e410",
  "status": "ready",
  "feedback": {
    "overall_abstention": null,
    "criteria": [
      {"criterion_id": "C1", "criterion_name": "Claim", "outcome": "feedback",
       "strength": "You open with a clear statement.",
       "next_step": "Name the benefit in one precise phrase.",
       "evidence": [{"start": 0, "end": 30, "quote": "Cool roofs can help a building"}],
       "abstention_reason": null},
      {"criterion_id": "C2", "criterion_name": "Evidence", "outcome": "abstain",
       "strength": null, "next_step": null, "evidence": [],
       "abstention_reason": "evidence_not_verified"},
      {"criterion_id": "C3", "criterion_name": "Reasoning", "outcome": "abstain",
       "strength": null, "next_step": null, "evidence": [],
       "abstention_reason": "not_assessable_from_response"}
    ]
  },
  "draft_text": "Claim:\nStrength: You open with a clear statement.\nNext step: Name the benefit in one precise phrase.",
  "review_flags": ["partial_abstention", "unverified_evidence_removed"],
  "provider": "fixture", "model_id": "deterministic-fixture",
  "prompt_version": "aeos-ela-feedback-draft-v1",
  "rubric_id": "RUB-CER3", "rubric_version": "0.1",
  "rubric_sha256": "8f7584b2ec1aa21cfc351e64b9907687b0e1c40570b452f8385f582741103861",
  "input_tokens": 900, "output_tokens": 200, "actual_cost_microusd": 7600,
  "data_classification": "synthetic",
  "decisions": [], "current_decision": null
}
```

(Abbreviated: the response also carries `organization_id`, `request_id`, `assessment_id`, `student_id`, `requested_by`, `response_text`, `response_model_id`, `error_code`, `created_at`.) The fixture deliberately cites an invented passage detail for C2 to show the removal path.

**Record the teacher decision**

```http
POST /ai-feedback/drafts/dfa8e18a-8dfc-460b-af8a-ba0ffe70e410/decisions
Idempotency-Key: 66666666-7777-4888-8999-000000000000

{"decision": "accepted",
 "approved_text": "Claim:\nStrength: You open with a clear statement.\nNext step: Name the benefit in one precise phrase.",
 "review_flags_acknowledged": true, "teacher_confirmed": true}
```

`201 Created` returns the same draft with `decisions[0].decision = "accepted"` and `current_decision` set. `revised` requires changed `approved_text`; `rejected` must omit it.

**Errors** always use `{"detail": {"code": "...", "message": "..."}}` (plus `draft_id` when an attempt was recorded):

| HTTP | `code` |
| --- | --- |
| 400 | `idempotency_key_required` |
| 403 | `organization_not_enabled`, `not_draft_owner` (an admin deciding another teacher's draft), and the existing role 403 for support users |
| 404 | existing tenant "not found" for foreign or missing ids, and for a same-organization draft the actor did not request (unless they are an admin) |
| 409 | `idempotency_key_reused`, `request_in_progress`, `decision_key_reused`, `draft_not_reviewable` |
| 422 | `rubric_not_found`, `rubric_not_approved`, `accepted_text_mismatch`, `revision_unchanged`, `accept_requires_ready_draft`, `review_flags_not_acknowledged`, request validation |
| 429 | `user_rate_limited`, `org_rate_limited`, `user_budget_exceeded`, `org_budget_exceeded` |
| 502 | `invalid_model_output` (with `reason`: `malformed_output`, `schema_violation`, `criteria_mismatch`, `prohibited_inference`, `truncated_output`), `provider_refused`, `provider_rejected_request`, `provider_error` |
| 503 | `feature_disabled`, `feature_misconfigured`, `provider_unavailable`, `provider_timeout`, `provider_rate_limited`, `provider_misconfigured`, `model_unavailable`, `model_unsupported` |

## Feature flag and configuration (backend environment only)

| Variable | Default | Notes |
| --- | --- | --- |
| `AEOS_AI_FEEDBACK_ENABLED` | `false` | Off → every route returns 503 `feature_disabled` |
| `AEOS_AI_FEEDBACK_MODEL` | *(none)* | Set an ID your provider account lists; checked live before use |
| `AEOS_AI_FEEDBACK_API_KEY` | *(none)* | Server secret; never sent to the browser |
| `AEOS_AI_FEEDBACK_INPUT_USD_PER_MTOK` / `..._OUTPUT_...` | *(none)* | Current prices for the configured model; required |
| `AEOS_AI_FEEDBACK_ORG_ALLOWLIST` | *(empty)* | Synthetic sandbox organizations only |
| `AEOS_AI_FEEDBACK_APPROVED_RUBRICS` | *(empty)* | `RUB-CER3@0.1:8f7584b2…3861` once a teacher has approved that exact content |
| `AEOS_AI_FEEDBACK_TIMEOUT_SECONDS` / `..._MAX_RETRIES` / `..._MAX_OUTPUT_TOKENS` | 30 / 2 / 4096 | Ceilings 120 / 3 / 16,000 |
| `AEOS_AI_FEEDBACK_USER_HOURLY_REQUESTS` / `..._ORG_DAILY_REQUESTS` | 10 / 100 | Rolling 1 h / 24 h |
| `AEOS_AI_FEEDBACK_USER_DAILY_COST_MICROUSD` / `..._ORG_DAILY_COST_MICROUSD` | 1,000,000 / 5,000,000 | $1 / $5 per rolling 24 h |

## Cost envelope

Reservation (worst case, charged against the budget before the call) = (UTF-8 bytes of instructions + rubric + data + schema + 1,000) × input price + `max_output_tokens` × output price. Byte-level tokenizers never produce more tokens than bytes, so this is an upper bound. After the call the actual `usage` cost replaces it. Prices below are **inputs you configure**, shown at three illustrative price points; confirm current prices for your model before enabling.

| Configured price (in / out per MTok) | Worst case (4,000-char response + 6,000-char source) | R01 + passage reservation | Illustrative actual at 3,000 in / 1,500 out tokens |
| --- | --- | --- | --- |
| $4 / $20 | $0.142 | $0.107 | $0.042 |
| $2 / $10 | $0.071 | $0.054 | $0.021 |
| $0.10 / $0.50 | $0.0036 | $0.0027 | $0.0011 |

The last column is arithmetic, not a measurement: no genuine provider call has been made. At $4 / $20 and the default caps, one user can hold about nine worst-case R01 reservations a day and an organization about 46, rising as actual costs are recorded. The hard ceiling is the configured daily caps.

## Actual results (local, 2026-10-11)

Environment: Python 3.11 with a fresh install of `backend/requirements-dev.txt` (incl. `anthropic==1.8.0`); PostgreSQL 16.15 (local, disposable); Node 22.22.0 / npm 10.9.4; Chromium 1194 (pre-installed).

| Check | Result |
| --- | --- |
| Baseline backend suite on the candidate before changes (RLS required) | 335 passed, 0 skipped |
| Full backend suite after changes (RLS required) | **521 passed, 0 skipped** (+99 workflow, +20 adapter, +33 migration-006 DB, +4 route auth, +30 RLS sweep cases over the new tables) |
| RLS enforcement module with 006 applied | 217 passed (was 187) |
| AI feedback slice mutation check (`docs/evidence/ai-feedback/`) | **17 / 17 killed** (first run 16/17; the survivor exposed a real gap, a replay during an outage, now tested) |
| Existing P0 security mutation contract | **37 / 37 killed**, 0 survived / invalid, migrations 001–006 applied (`docs/evidence/ai-feedback/p0-mutation-matrix-with-006.json`; run on `fd0a756`, full suite 521 cases per mutant) |
| `compileall`, mutation anchors | pass; 37 anchors |
| Frontend request contracts | 6 new + 6 existing passed; lint-glob guards 3 passed |
| `npm run lint`, `tsc --noEmit`, `npm run build` | pass, pass, pass |
| `npm audit --audit-level=low` (full and `--omit=dev`) | **FAIL, pre-existing:** `next@16.3.6` (6 advisories, fixed in 16.3.8) and `sharp` < 0.35.5. This change does not modify `package.json` or the lockfile. |
| Browser walk-through (Chromium, built frontend, fixture server) | **12 / 12** checks passed; screenshot in `docs/evidence/ai-feedback/` |
| Genuine provider smoke check | **BLOCKED**: no provider key, model or prices are configured for this project. `api.anthropic.com/v1/models` is reachable (HTTP 401 unauthenticated). This session's own credentials were deliberately not used. |
| CI | The P0 workflow triggers on pushes to `p0/security-*` and PRs to `main`; this stacked branch triggers neither, so **no CI run exists for it**. |

## Remaining evaluation gates

| Gate | State | What closes it |
| --- | --- | --- |
| Teacher approval of the rubric | **BLOCKED** | A teacher reviews RUB-CER3 v0.1 (or a replacement), then the approver pins its hash in `AEOS_AI_FEEDBACK_APPROVED_RUBRICS`. Until then the server refuses every request. |
| Genuine provider smoke check | **BLOCKED** | Run `python -m tests.ai_feedback_provider_smoke` with a server-side key, a confirmed model ID and current prices; record the JSON output. |
| Feedback quality evaluation | **NOT STARTED** | Hypothesis, baseline (teacher-written feedback), labeled synthetic set incl. the PR #30 hidden key, thresholds for evidence-span validity, criterion alignment, abstention appropriateness, prohibited-inference false-positive and false-negative rates, and teacher accept/revise/reject rates. No accuracy claim before this passes. |
| Prohibited-language filter calibration | Open | The regex filter is conservative and will reject some acceptable drafts (e.g. feedback using "grade level"); measure the false-rejection rate on the evaluation set. |
| Dependency audit | **BLOCKED (pre-existing)** | Candidate-level Next.js/sharp remediation in its own reviewed change. |
| CI on an exact head | Open | Run the workflow on this head (or after it is folded into a `p0/security-*` candidate) and reconcile counts. |
| Hosted Supabase tenant gate | **BLOCKED (pre-existing)** | Apply 001–006 to an isolated hosted project and repeat the two-tenant attacks. Local PostgreSQL is not a substitute. |
| Independent verification | Open | A fresh session verifies this exact head; this builder session cannot. |
| Real student data | **BLOCKED** | Consent, data-processing agreement, retention policy for `ai_feedback_requests.response_text`, and the gates above. |
| P-TER-01 reconciliation | Open | See [`docs/pilots/p-ter-01/`](pilots/p-ter-01/README.md): v0.3 source not located, owner decisions D1–D5, review of the unapproved attendance candidate, and the `0` / `IE` / abstention boundaries. |

## Out of scope by design

No automatic gradebook writes, no IEP generation, no messages to students or families, no score or rubric-level suggestion, no merge and no launch.

## Reproduction

```bash
cd backend
pip install -r requirements-dev.txt
export AEOS_REQUIRE_RLS_TESTS=1 AEOS_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
python -m pytest tests/ -q -rs
python -m pytest tests/test_ai_feedback.py tests/test_ai_feedback_provider.py tests/test_ai_feedback_rls.py -q
cd ../frontend && npm ci && node --experimental-vm-modules tests/ai-feedback-api.test.mjs && npm run lint && npx tsc --noEmit && npm run build
cd .. && python docs/evidence/ai-feedback/feedback_mutations.py . "$(command -v python)"
```
