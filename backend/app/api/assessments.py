from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.supabase_service import get_supabase_admin_client

router = APIRouter(prefix="/assessments", tags=["assessments"])


class AssessmentCreateRequest(BaseModel):
    organization_id: str = Field(..., min_length=1)
    student_id: str = Field(..., min_length=1)
    created_by: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    assessment_type: str = Field(..., min_length=1)
    status: str = Field(default="draft", min_length=1)
    notes: Optional[str] = None


class AssessmentResponse(BaseModel):
    id: str
    organization_id: str
    student_id: str
    created_by: str
    title: str
    assessment_type: str
    status: str
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(payload: AssessmentCreateRequest):
    client = get_supabase_admin_client()
    response = client.table("assessments").insert(payload.model_dump(exclude_none=True)).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Assessment could not be created")

    return AssessmentResponse(**response.data[0])


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: str):
    client = get_supabase_admin_client()
    response = client.table("assessments").select("*").eq("id", assessment_id).limit(1).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return AssessmentResponse(**response.data[0])


class AssessmentAnalysisRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    assessment_type: str = Field(..., min_length=1)
    score: Optional[float] = None
    notes: Optional[str] = None


class AssessmentAnalysisResponse(BaseModel):
    student_id: str
    assessment_type: str
    status: str
    summary: str
    recommended_intervention: str
    note: str


@router.post("/analyze", response_model=AssessmentAnalysisResponse)
def analyze_assessment(payload: AssessmentAnalysisRequest):
    # Placeholder logic only; AI integration will be added later.
    summary = (
        f"Assessment analysis placeholder for student {payload.student_id}. "
        f"Assessment type: {payload.assessment_type}."
    )

    if payload.score is not None:
        summary += f" Score received: {payload.score}."

    if payload.notes:
        summary += f" Notes provided: {payload.notes}"

    return AssessmentAnalysisResponse(
        student_id=payload.student_id,
        assessment_type=payload.assessment_type,
        status="pending_placeholder",
        summary=summary,
        recommended_intervention="Review student context and confirm next-step support plan.",
        note="AI integration is not implemented yet; this endpoint returns placeholder analysis.",
    )
