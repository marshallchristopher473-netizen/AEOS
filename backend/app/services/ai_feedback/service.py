"""Teacher feedback-drafting workflow.

    synthetic response -> AI draft (immutable) -> teacher review
        -> accept / revise / reject (explicit, append-only) -> official record

Every query uses the server-derived organization. Identity, organization,
student and authorship are never taken from the request body.

A draft belongs to the teacher who requested it. Inside the organization only
that teacher and org admins may read it, and only that teacher may decide it.
Migration 007 enforces the same rule in the database.
"""

import hashlib
import json
import logging
import uuid
from decimal import ROUND_CEILING, Decimal
from typing import Any, Callable, Dict, List, Optional, Tuple

from fastapi import HTTPException, status

from app.core.ai_feedback_settings import AiFeedbackSettings
from app.models.ai_feedback import (
    AiFeedbackDecisionCreateRequest,
    AiFeedbackDecisionResponse,
    AiFeedbackDraftCreateRequest,
    AiFeedbackDraftResponse,
    provider_output_json_schema,
)
from app.models.schemas import AuthenticatedActor
from app.services.ai_feedback.prompt import (
    PROMPT_VERSION,
    SYSTEM_INSTRUCTIONS,
    build_user_content,
    has_embedded_instructions,
)
from app.services.ai_feedback.provider import (
    FeedbackProvider,
    ProviderError,
    checked_model,
)
from app.services.ai_feedback.rubrics import (
    RubricNotApproved,
    RubricNotFound,
    get_approved_rubric,
)
from app.services.ai_feedback.validation import OutputRejected, validate_provider_output
from app.services.tenant_scope import (
    assert_related_row_in_tenant,
    get_tenant_scoped_row,
    list_tenant_scoped_rows,
)

logger = logging.getLogger("aeos.ai_feedback")

REQUESTS = "ai_feedback_requests"
DRAFTS = "ai_feedback_drafts"
DECISIONS = "ai_feedback_decisions"
RESERVE_FUNCTION = "aeos_reserve_ai_feedback_request"

# Structured-output mode adds provider-side framing that is not in our text.
# This allowance keeps the reservation an upper bound.
INPUT_OVERHEAD_TOKENS = 1000

REVIEWABLE_STATUSES = ("ready", "abstained")

DRAFT_NOT_FOUND = "Draft not found"

_MESSAGES = {
    "feature_disabled": "AI feedback drafting is not enabled.",
    "feature_misconfigured": "AI feedback drafting is not available right now.",
    "organization_not_enabled": "AI feedback drafting is not enabled for this organization.",
    "idempotency_key_required": "An Idempotency-Key header containing a UUID is required.",
    "idempotency_key_reused": "This Idempotency-Key was already used for a different request.",
    "request_in_progress": "This request is still being processed or did not finish. Start a new request.",
    "rubric_not_found": "That rubric version does not exist.",
    "rubric_not_approved": "That rubric version has not been approved for use.",
    "user_rate_limited": "You have reached the hourly limit for AI drafts. Try again later.",
    "org_rate_limited": "Your organization has reached its daily limit for AI drafts.",
    "user_budget_exceeded": "You have reached the daily spending limit for AI drafts.",
    "org_budget_exceeded": "Your organization has reached its daily spending limit for AI drafts.",
    "provider_unavailable": "The AI provider is unavailable. Try again later.",
    "provider_timeout": "The AI provider did not respond in time. Try again later.",
    "provider_rate_limited": "The AI provider is busy. Try again later.",
    "provider_misconfigured": "AI feedback drafting is not available right now.",
    "model_unavailable": "The configured AI model is not available.",
    "model_unsupported": "The configured AI model does not support this workflow.",
    "provider_refused": "The AI provider declined to draft feedback for this response.",
    "provider_rejected_request": "The AI provider rejected the request.",
    "provider_error": "The AI provider returned an error.",
    "invalid_model_output": "The AI output failed safety validation and was discarded. Write feedback yourself or try again.",
    "draft_not_saved": "The draft could not be saved.",
    "draft_not_reviewable": "This draft has no reviewable output.",
    "not_draft_owner": "Only the teacher who requested this draft can record a decision on it.",
    "accepted_text_mismatch": "Accepted text must match the draft exactly. Use 'revised' to save changes.",
    "accept_requires_ready_draft": "There is no AI draft text to accept. Revise with your own text or reject.",
    "revision_unchanged": "The revised text matches the draft. Use 'accepted' instead.",
    "review_flags_not_acknowledged": "Acknowledge the review flags before saving feedback.",
    "decision_key_reused": "This Idempotency-Key was already used for a different decision.",
    "decision_not_saved": "The decision could not be saved.",
}


def api_error(http_status: int, code: str, **extra: Any) -> HTTPException:
    return HTTPException(
        status_code=http_status,
        detail={"code": code, "message": _MESSAGES.get(code, "Request failed."), **extra},
    )


def parse_idempotency_key(raw: Optional[str]) -> str:
    try:
        return str(uuid.UUID(str(raw)))
    except (TypeError, ValueError):
        raise api_error(status.HTTP_400_BAD_REQUEST, "idempotency_key_required")


def canonical_sha256(document: Dict[str, Any]) -> str:
    canonical = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _microusd(amount: Decimal) -> int:
    return int(amount.to_integral_value(rounding=ROUND_CEILING))


def reservation_microusd(settings: AiFeedbackSettings, *prompt_parts: str) -> int:
    """Worst-case cost. Byte-level tokenizers never emit more tokens than
    input bytes, so UTF-8 length bounds input tokens; output is bounded by
    max_output_tokens. USD per million tokens equals micro-USD per token."""
    input_upper = sum(len(part.encode("utf-8")) for part in prompt_parts) + INPUT_OVERHEAD_TOKENS
    return _microusd(
        Decimal(input_upper) * settings.input_usd_per_mtok
        + Decimal(settings.max_output_tokens) * settings.output_usd_per_mtok
    )


def actual_microusd(settings: AiFeedbackSettings, input_tokens: int, output_tokens: int) -> int:
    return _microusd(
        Decimal(input_tokens) * settings.input_usd_per_mtok
        + Decimal(output_tokens) * settings.output_usd_per_mtok
    )


def _first(response) -> Optional[Dict[str, Any]]:
    data = response.data or []
    return data[0] if data else None


class AiFeedbackService:
    def __init__(
        self,
        client,
        settings: AiFeedbackSettings,
        provider_factory: Optional[Callable[[AiFeedbackSettings], FeedbackProvider]] = None,
    ):
        self.client = client
        self.settings = settings
        self.provider_factory = provider_factory

    # -- gates ---------------------------------------------------------------

    def ensure_available(self, actor: AuthenticatedActor, for_generation: bool = False) -> None:
        if not self.settings.enabled:
            raise api_error(status.HTTP_503_SERVICE_UNAVAILABLE, "feature_disabled")
        if for_generation:
            problems = self.settings.configuration_errors()
            if problems:
                logger.error("ai_feedback misconfigured: %s", ",".join(problems))
                raise api_error(status.HTTP_503_SERVICE_UNAVAILABLE, "feature_misconfigured")
        if actor.organization_id not in self.settings.organization_allowlist:
            raise api_error(status.HTTP_403_FORBIDDEN, "organization_not_enabled")

    # -- ownership -----------------------------------------------------------

    @staticmethod
    def _can_read(actor: AuthenticatedActor, request_row: Dict[str, Any]) -> bool:
        return request_row["created_by"] == actor.user_id or actor.role == "admin"

    def _load_readable(
        self, draft_id: str, actor: AuthenticatedActor
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Return (draft, request) or 404. A draft the actor may not read is
        reported exactly like one that does not exist."""
        draft_row = get_tenant_scoped_row(self.client, DRAFTS, draft_id, actor.organization_id, DRAFT_NOT_FOUND)
        request_row = get_tenant_scoped_row(
            self.client, REQUESTS, draft_row["request_id"], actor.organization_id, DRAFT_NOT_FOUND
        )
        if not self._can_read(actor, request_row):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=DRAFT_NOT_FOUND)
        return draft_row, request_row

    # -- reads ---------------------------------------------------------------

    def _decisions_for(self, organization_id: str, draft_id: str) -> List[Dict[str, Any]]:
        rows = list(
            self.client.table(DECISIONS)
            .select("*")
            .eq("organization_id", organization_id)
            .eq("draft_id", draft_id)
            .execute()
            .data
            or []
        )
        return [row for _, row in sorted(enumerate(rows), key=lambda pair: (pair[1].get("created_at") or "", pair[0]))]

    def _to_response(
        self,
        request_row: Dict[str, Any],
        draft_row: Dict[str, Any],
        decision_rows: List[Dict[str, Any]],
    ) -> AiFeedbackDraftResponse:
        decisions = [AiFeedbackDecisionResponse(**row) for row in decision_rows]
        return AiFeedbackDraftResponse(
            id=draft_row["id"],
            organization_id=draft_row["organization_id"],
            request_id=request_row["id"],
            assessment_id=request_row["assessment_id"],
            student_id=request_row["student_id"],
            requested_by=request_row["created_by"],
            status=draft_row["status"],
            feedback=draft_row.get("output"),
            draft_text=draft_row.get("draft_text"),
            review_flags=list(draft_row.get("review_flags") or []),
            error_code=draft_row.get("error_code"),
            response_text=request_row["response_text"],
            provider=request_row["provider"],
            model_id=request_row["model_id"],
            response_model_id=draft_row.get("response_model_id"),
            prompt_version=request_row["prompt_version"],
            rubric_id=request_row["rubric_id"],
            rubric_version=request_row["rubric_version"],
            rubric_sha256=request_row["rubric_sha256"],
            input_tokens=draft_row.get("input_tokens"),
            output_tokens=draft_row.get("output_tokens"),
            actual_cost_microusd=draft_row.get("actual_cost_microusd") or 0,
            data_classification=request_row["data_classification"],
            decisions=decisions,
            current_decision=decisions[-1] if decisions else None,
            created_at=draft_row.get("created_at"),
        )

    def get_draft(self, draft_id: str, actor: AuthenticatedActor) -> AiFeedbackDraftResponse:
        draft_row, request_row = self._load_readable(draft_id, actor)
        return self._to_response(request_row, draft_row, self._decisions_for(actor.organization_id, draft_id))

    def list_drafts(self, assessment_id: str, actor: AuthenticatedActor) -> List[AiFeedbackDraftResponse]:
        assert_related_row_in_tenant(
            self.client, "assessments", assessment_id, actor.organization_id, "Assessment not found"
        )
        requests_by_id = {
            row["id"]: row
            for row in list_tenant_scoped_rows(self.client, REQUESTS, actor.organization_id)
            if row["assessment_id"] == assessment_id and self._can_read(actor, row)
        }
        decisions: Dict[str, List[Dict[str, Any]]] = {}
        for index, row in enumerate(list_tenant_scoped_rows(self.client, DECISIONS, actor.organization_id)):
            decisions.setdefault(row["draft_id"], []).append((row.get("created_at") or "", index, row))
        drafts = [
            row
            for row in list_tenant_scoped_rows(self.client, DRAFTS, actor.organization_id)
            if row["request_id"] in requests_by_id
        ]
        return [
            self._to_response(
                requests_by_id[row["request_id"]],
                row,
                [item[2] for item in sorted(decisions.get(row["id"], []), key=lambda item: item[:2])],
            )
            for row in drafts
        ]

    # -- generation ----------------------------------------------------------

    def _existing_request(self, actor: AuthenticatedActor, request_key: str) -> Optional[Dict[str, Any]]:
        return _first(
            self.client.table(REQUESTS)
            .select("*")
            .eq("organization_id", actor.organization_id)
            .eq("created_by", actor.user_id)
            .eq("request_key", request_key)
            .limit(1)
            .execute()
        )

    def _draft_for_request(self, organization_id: str, request_id: str) -> Optional[Dict[str, Any]]:
        return _first(
            self.client.table(DRAFTS)
            .select("*")
            .eq("organization_id", organization_id)
            .eq("request_id", request_id)
            .limit(1)
            .execute()
        )

    def _outcome(
        self, request_row: Dict[str, Any], draft_row: Dict[str, Any], created: bool
    ) -> Tuple[AiFeedbackDraftResponse, bool]:
        """Map a stored outcome to the HTTP result. A replay returns the same
        outcome as the original call, without calling the provider again."""
        draft_status = draft_row["status"]
        if draft_status in REVIEWABLE_STATUSES:
            return self._to_response(request_row, draft_row, self._decisions_for(draft_row["organization_id"], draft_row["id"])), created
        code = draft_row.get("error_code") or "provider_error"
        if draft_status == "rejected_output":
            raise api_error(status.HTTP_502_BAD_GATEWAY, "invalid_model_output", draft_id=draft_row["id"], reason=code)
        http_status = (
            status.HTTP_503_SERVICE_UNAVAILABLE
            if code in ("provider_unavailable", "provider_timeout", "provider_rate_limited",
                        "provider_misconfigured", "model_unavailable", "model_unsupported")
            else status.HTTP_502_BAD_GATEWAY
        )
        raise api_error(http_status, code, draft_id=draft_row["id"])

    def _replay(self, existing: Dict[str, Any], input_sha256: str) -> Tuple[AiFeedbackDraftResponse, bool]:
        if existing["input_sha256"] != input_sha256:
            raise api_error(status.HTTP_409_CONFLICT, "idempotency_key_reused")
        draft_row = self._draft_for_request(existing["organization_id"], existing["id"])
        if draft_row is None:
            raise api_error(status.HTTP_409_CONFLICT, "request_in_progress")
        return self._outcome(existing, draft_row, created=False)

    def _insert_draft(self, row: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.client.table(DRAFTS).insert(row).execute()
        except Exception:  # noqa: BLE001 - reported without content
            logger.exception("ai_feedback draft insert failed request_id=%s", row.get("request_id"))
            raise api_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "draft_not_saved")
        saved = _first(response)
        if saved is None:
            raise api_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "draft_not_saved")
        return saved

    def create_draft(
        self,
        payload: AiFeedbackDraftCreateRequest,
        request_key: str,
        actor: AuthenticatedActor,
    ) -> Tuple[AiFeedbackDraftResponse, bool]:
        self.ensure_available(actor, for_generation=True)
        settings = self.settings

        assessment = assert_related_row_in_tenant(
            self.client, "assessments", payload.assessment_id, actor.organization_id, "Assessment not found"
        )
        try:
            rubric = get_approved_rubric(payload.rubric_id, payload.rubric_version, settings.approved_rubrics)
        except RubricNotFound:
            raise api_error(status.HTTP_422_UNPROCESSABLE_ENTITY, "rubric_not_found")
        except RubricNotApproved:
            raise api_error(status.HTTP_422_UNPROCESSABLE_ENTITY, "rubric_not_approved")

        input_sha256 = canonical_sha256(
            {
                "assessment_id": payload.assessment_id,
                "rubric_id": rubric.id,
                "rubric_version": rubric.version,
                "rubric_sha256": rubric.sha256,
                "response_text": payload.response_text,
                "source_text": payload.source_text,
                "data_classification": payload.data_classification,
            }
        )

        existing = self._existing_request(actor, request_key)
        if existing is not None:
            return self._replay(existing, input_sha256)

        provider = self.provider_factory(settings)
        try:
            checked_model(provider, settings)
        except ProviderError as exc:
            # Nothing was reserved or spent; no draft row is written.
            raise api_error(exc.http_status, exc.code)

        user_content = build_user_content(rubric, payload.response_text, payload.source_text)
        schema = provider_output_json_schema(list(rubric.criterion_ids))
        request_row = {
            "id": str(uuid.uuid4()),
            "organization_id": actor.organization_id,
            "assessment_id": payload.assessment_id,
            "student_id": assessment["student_id"],
            "created_by": actor.user_id,
            "request_key": request_key,
            "input_sha256": input_sha256,
            "data_classification": payload.data_classification,
            "response_text": payload.response_text,
            "source_text": payload.source_text,
            "rubric_id": rubric.id,
            "rubric_version": rubric.version,
            "rubric_sha256": rubric.sha256,
            "prompt_version": PROMPT_VERSION,
            "provider": provider.name,
            "model_id": settings.model_id,
            "reserved_cost_microusd": reservation_microusd(
                settings, SYSTEM_INSTRUCTIONS, user_content, json.dumps(schema)
            ),
        }

        reservation = self.client.rpc(
            RESERVE_FUNCTION, {"p_request": request_row, "p_limits": settings.limits()}
        ).execute().data
        if isinstance(reservation, list):
            reservation = reservation[0] if reservation else {}
        outcome = (reservation or {}).get("outcome")
        if outcome == "duplicate":
            existing = self._existing_request(actor, request_key)
            if existing is None:
                raise api_error(status.HTTP_409_CONFLICT, "request_in_progress")
            return self._replay(existing, input_sha256)
        if outcome in ("user_rate_limited", "org_rate_limited", "user_budget_exceeded", "org_budget_exceeded"):
            raise api_error(status.HTTP_429_TOO_MANY_REQUESTS, outcome)
        if outcome != "reserved" or reservation.get("request_id") != request_row["id"]:
            logger.error("ai_feedback reservation returned an unexpected outcome")
            raise api_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "draft_not_saved")

        draft_row: Dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "organization_id": actor.organization_id,
            "request_id": request_row["id"],
            "output": None,
            "draft_text": None,
            "review_flags": [],
            "error_code": None,
            "response_model_id": None,
            "input_tokens": None,
            "output_tokens": None,
            "actual_cost_microusd": 0,
        }

        try:
            completion = provider.complete(
                model_id=settings.model_id,
                system=SYSTEM_INSTRUCTIONS,
                user_content=user_content,
                output_schema=schema,
                max_output_tokens=settings.max_output_tokens,
            )
        except ProviderError as exc:
            draft_row.update(status="provider_error", error_code=exc.code)
            return self._outcome(request_row, self._insert_draft(draft_row), created=True)

        draft_row.update(
            response_model_id=completion.response_model_id,
            input_tokens=completion.input_tokens,
            output_tokens=completion.output_tokens,
            actual_cost_microusd=actual_microusd(settings, completion.input_tokens, completion.output_tokens),
        )
        input_flags = (
            ["possible_embedded_instructions"]
            if has_embedded_instructions(payload.response_text, payload.source_text)
            else []
        )

        if completion.stop_reason == "refusal":
            draft_row.update(status="provider_refused", error_code="provider_refused")
        elif completion.stop_reason == "max_tokens":
            draft_row.update(status="rejected_output", error_code="truncated_output")
        elif completion.text is None:
            draft_row.update(status="rejected_output", error_code="malformed_output")
        else:
            try:
                validated = validate_provider_output(
                    completion.text, rubric, payload.response_text, input_flags
                )
            except OutputRejected as exc:
                draft_row.update(status="rejected_output", error_code=exc.code)
            else:
                draft_row.update(
                    status=validated.status,
                    output=validated.feedback.model_dump(),
                    draft_text=validated.draft_text,
                    review_flags=validated.review_flags,
                )

        if draft_row["status"] not in REVIEWABLE_STATUSES:
            draft_row["review_flags"] = input_flags
        return self._outcome(request_row, self._insert_draft(draft_row), created=True)

    # -- teacher decision ----------------------------------------------------

    def _existing_decision(self, actor: AuthenticatedActor, decision_key: str) -> Optional[Dict[str, Any]]:
        return _first(
            self.client.table(DECISIONS)
            .select("*")
            .eq("organization_id", actor.organization_id)
            .eq("decided_by", actor.user_id)
            .eq("decision_key", decision_key)
            .limit(1)
            .execute()
        )

    def record_decision(
        self,
        draft_id: str,
        payload: AiFeedbackDecisionCreateRequest,
        decision_key: str,
        actor: AuthenticatedActor,
    ) -> Tuple[AiFeedbackDraftResponse, bool]:
        self.ensure_available(actor)
        draft_row, request_row = self._load_readable(draft_id, actor)
        # An admin can read another teacher's draft but may not decide it.
        if request_row["created_by"] != actor.user_id:
            raise api_error(status.HTTP_403_FORBIDDEN, "not_draft_owner")

        payload_sha256 = canonical_sha256(
            {
                "draft_id": draft_id,
                "decision": payload.decision,
                "approved_text": payload.approved_text,
                "review_flags_acknowledged": payload.review_flags_acknowledged,
            }
        )
        existing = self._existing_decision(actor, decision_key)
        if existing is not None:
            if existing["payload_sha256"] != payload_sha256:
                raise api_error(status.HTTP_409_CONFLICT, "decision_key_reused")
            return self.get_draft(draft_id, actor), False

        if draft_row["status"] not in REVIEWABLE_STATUSES:
            raise api_error(status.HTTP_409_CONFLICT, "draft_not_reviewable")
        draft_text = draft_row.get("draft_text")
        if payload.decision == "accepted":
            if draft_row["status"] != "ready" or not draft_text:
                raise api_error(status.HTTP_422_UNPROCESSABLE_ENTITY, "accept_requires_ready_draft")
            if payload.approved_text != draft_text:
                raise api_error(status.HTTP_422_UNPROCESSABLE_ENTITY, "accepted_text_mismatch")
        if payload.decision == "revised" and draft_text and payload.approved_text.strip() == draft_text.strip():
            raise api_error(status.HTTP_422_UNPROCESSABLE_ENTITY, "revision_unchanged")
        if (
            payload.decision != "rejected"
            and draft_row.get("review_flags")
            and not payload.review_flags_acknowledged
        ):
            raise api_error(status.HTTP_422_UNPROCESSABLE_ENTITY, "review_flags_not_acknowledged")

        row = {
            "id": str(uuid.uuid4()),
            "organization_id": actor.organization_id,
            "draft_id": draft_id,
            "decided_by": actor.user_id,
            "decision": payload.decision,
            "approved_text": payload.approved_text,
            "review_flags_acknowledged": payload.review_flags_acknowledged,
            "teacher_confirmed": True,
            "decision_key": decision_key,
            "payload_sha256": payload_sha256,
        }
        try:
            saved = _first(self.client.table(DECISIONS).insert(row).execute())
        except Exception:  # noqa: BLE001 - a concurrent duplicate is resolved below
            saved = None
            existing = self._existing_decision(actor, decision_key)
            if existing is not None and existing["payload_sha256"] == payload_sha256:
                return self.get_draft(draft_id, actor), False
            logger.exception("ai_feedback decision insert failed draft_id=%s", draft_id)
        if saved is None:
            raise api_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "decision_not_saved")
        return self._to_response(
            request_row, draft_row, self._decisions_for(actor.organization_id, draft_id)
        ), True
