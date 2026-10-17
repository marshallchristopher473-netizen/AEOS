from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AuthenticatedActor(BaseModel):
    """Server-derived identity and authorization context."""

    user_id: str = Field(..., min_length=1)
    organization_id: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    auth_user_id: str = Field(..., min_length=1)


class AssessmentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: str = Field(..., min_length=1)
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


class AssessmentResultCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment_id: str = Field(..., min_length=1)
    score: Optional[float] = Field(default=None, ge=0, le=9999.99, allow_inf_nan=False)
    max_score: Optional[float] = Field(default=None, ge=0.01, le=9999.99, allow_inf_nan=False)
    summary: Optional[str] = None
    status: Literal["draft", "submitted", "in_review", "complete"] = "draft"

    @model_validator(mode="after")
    def validate_score_range(self):
        if self.score is not None and self.max_score is not None:
            if self.score > self.max_score:
                raise ValueError("Score must not exceed the maximum score")
        return self


class AssessmentResultResponse(BaseModel):
    id: str
    organization_id: str
    assessment_id: str
    student_id: str
    created_by: str
    score: Optional[float] = None
    max_score: Optional[float] = None
    summary: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
