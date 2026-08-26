from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_actor
from app.models.schemas import AssessmentCreateRequest, AssessmentResponse, AuthenticatedActor
from app.services.assessment_service import AssessmentService
from app.services.supabase_service import get_supabase_admin_client
from app.services.tenant_scope import assert_related_row_in_tenant

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreateRequest,
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    assert_related_row_in_tenant(
        client,
        "students",
        payload.student_id,
        actor.organization_id,
        "Student not found",
    )
    service = AssessmentService(client)
    return service.create_assessment(
        {**payload.model_dump(exclude_none=True), "created_by": actor.user_id},
        actor.organization_id,
    )


@router.get("", response_model=list[AssessmentResponse])
def list_assessments(
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    return AssessmentService(client).list_assessments(actor.organization_id)


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: str,
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    return AssessmentService(client).get_assessment(
        assessment_id,
        actor.organization_id,
    )
