from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AuthenticatedActor(BaseModel):
    """Trusted server-derived identity for the current request.

    Populated only from the AEOS `users` row resolved via the JWT's `sub`
    claim (see `app.core.dependencies.get_current_actor`) — never from
    client-supplied request data.
    """

    user_id: str
    organization_id: str
    role: str
    auth_user_id: str


class AssessmentCreateRequest(BaseModel):
    """organization_id and created_by are intentionally absent: they are
    derived server-side from the authenticated actor
    (see app.core.dependencies.get_current_actor), never accepted from the
    client. extra="forbid" rejects a client that still sends them (or any
    other unrecognized field) with a 422, rather than silently ignoring
    the value."""

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
