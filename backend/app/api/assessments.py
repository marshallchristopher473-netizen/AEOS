from fastapi import APIRouter, status

from app.models.schemas import AssessmentCreateRequest, AssessmentResponse
from app.services.assessment_service import AssessmentService
from app.services.supabase_service import get_supabase_admin_client

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(payload: AssessmentCreateRequest):
    service = AssessmentService(get_supabase_admin_client())
    return service.create_assessment(payload)


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: str):
    service = AssessmentService(get_supabase_admin_client())
    return service.get_assessment(assessment_id)
