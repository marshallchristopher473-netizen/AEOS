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
    # The referenced student must belong to the actor's own organization -
    # otherwise this would let one tenant attach an assessment to another
    # tenant's student. 404 (not 403/400) so a cross-tenant id doesn't
    # confirm its own existence.
    assert_related_row_in_tenant(
        client,
        "students",
        payload.student_id,
        actor.organization_id,
        not_found_detail="Student not found",
    )

    record = {
        **payload.model_dump(exclude_none=True),
        "organization_id": actor.organization_id,
        "created_by": actor.user_id,
    }

    service = AssessmentService(client)
    return service.create_assessment(record)


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: str,
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    service = AssessmentService(client)
    return service.get_assessment(assessment_id, actor.organization_id)
