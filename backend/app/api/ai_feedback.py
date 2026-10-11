from fastapi import APIRouter, Depends, Header, Query, Response, status

from app.core.ai_feedback_settings import AiFeedbackSettings, get_ai_feedback_settings
from app.core.dependencies import get_current_actor, require_privileged_write
from app.models.ai_feedback import (
    AiFeedbackDecisionCreateRequest,
    AiFeedbackDraftCreateRequest,
    AiFeedbackDraftResponse,
)
from app.models.schemas import AuthenticatedActor
from app.services.ai_feedback.provider import get_feedback_provider_factory
from app.services.ai_feedback.service import AiFeedbackService, parse_idempotency_key
from app.services.supabase_service import get_supabase_admin_client

router = APIRouter(prefix="/ai-feedback", tags=["ai-feedback"])


@router.post(
    "/drafts",
    response_model=AiFeedbackDraftResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_feedback_draft(
    payload: AiFeedbackDraftCreateRequest,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    actor: AuthenticatedActor = Depends(require_privileged_write),
    client=Depends(get_supabase_admin_client),
    settings: AiFeedbackSettings = Depends(get_ai_feedback_settings),
    provider_factory=Depends(get_feedback_provider_factory),
):
    """Draft criterion-linked feedback for one synthetic response.

    Returns 201 for a new draft and 200 when the same Idempotency-Key and
    payload are replayed; the provider is never called twice for one key.
    """
    service = AiFeedbackService(client, settings, provider_factory)
    service.ensure_available(actor, for_generation=True)
    draft, created = service.create_draft(payload, parse_idempotency_key(idempotency_key), actor)
    if not created:
        response.status_code = status.HTTP_200_OK
    return draft


@router.get("/drafts", response_model=list[AiFeedbackDraftResponse])
def list_feedback_drafts(
    assessment_id: str = Query(..., min_length=1),
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
    settings: AiFeedbackSettings = Depends(get_ai_feedback_settings),
):
    service = AiFeedbackService(client, settings)
    service.ensure_available(actor)
    return service.list_drafts(assessment_id, actor)


@router.get("/drafts/{draft_id}", response_model=AiFeedbackDraftResponse)
def get_feedback_draft(
    draft_id: str,
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
    settings: AiFeedbackSettings = Depends(get_ai_feedback_settings),
):
    service = AiFeedbackService(client, settings)
    service.ensure_available(actor)
    return service.get_draft(draft_id, actor)


@router.post(
    "/drafts/{draft_id}/decisions",
    response_model=AiFeedbackDraftResponse,
    status_code=status.HTTP_201_CREATED,
)
def record_feedback_decision(
    draft_id: str,
    payload: AiFeedbackDecisionCreateRequest,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    actor: AuthenticatedActor = Depends(require_privileged_write),
    client=Depends(get_supabase_admin_client),
    settings: AiFeedbackSettings = Depends(get_ai_feedback_settings),
):
    """Record an explicit teacher decision. Append-only: each call adds a row
    and the latest row is the current decision."""
    service = AiFeedbackService(client, settings)
    service.ensure_available(actor)
    draft, created = service.record_decision(
        draft_id, payload, parse_idempotency_key(idempotency_key), actor
    )
    if not created:
        response.status_code = status.HTTP_200_OK
    return draft
