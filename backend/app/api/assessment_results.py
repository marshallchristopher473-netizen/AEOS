from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_actor, require_privileged_write
from app.models.schemas import (
    AssessmentResultCreateRequest,
    AssessmentResultResponse,
    AuthenticatedActor,
)
from app.services.assessment_result_service import AssessmentResultService
from app.services.supabase_service import get_supabase_admin_client

router = APIRouter(prefix="/assessment-results", tags=["assessment-results"])


@router.post("", response_model=AssessmentResultResponse, status_code=status.HTTP_201_CREATED)
def create_assessment_result(
    payload: AssessmentResultCreateRequest,
    actor: AuthenticatedActor = Depends(require_privileged_write),
    client=Depends(get_supabase_admin_client),
):
    service = AssessmentResultService(client)
    return service.create_assessment_result(
        {**payload.model_dump(exclude_none=True), "created_by": actor.user_id},
        actor.organization_id,
    )


@router.get("", response_model=list[AssessmentResultResponse])
def list_assessment_results(
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    return AssessmentResultService(client).list_assessment_results(actor.organization_id)


@router.get("/{assessment_result_id}", response_model=AssessmentResultResponse)
def get_assessment_result(
    assessment_result_id: str,
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    return AssessmentResultService(client).get_assessment_result(
        assessment_result_id,
        actor.organization_id,
    )
