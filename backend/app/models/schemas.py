from typing import Optional

from pydantic import BaseModel, Field


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
