from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field

from app.core.dependencies import get_current_actor
from app.models.schemas import AuthenticatedActor
from app.services.supabase_service import get_supabase_admin_client
from app.services.tenant_scope import (
    assert_related_row_in_tenant,
    get_tenant_scoped_row,
    insert_tenant_scoped_row,
    list_tenant_scoped_rows,
)

router = APIRouter(prefix="/students", tags=["students"])


class StudentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    school_id: Optional[str] = None
    student_number: Optional[str] = None
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    grade_level: Optional[str] = None
    iep_status: bool = False
    birth_date: Optional[str] = None


class StudentResponse(BaseModel):
    id: str
    organization_id: str
    school_id: Optional[str] = None
    student_number: Optional[str] = None
    first_name: str
    last_name: str
    grade_level: Optional[str] = None
    iep_status: bool = False
    birth_date: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    payload: StudentCreateRequest,
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    if payload.school_id:
        assert_related_row_in_tenant(
            client,
            "schools",
            payload.school_id,
            actor.organization_id,
            "School not found",
        )

    row = insert_tenant_scoped_row(
        client,
        "students",
        {
            **payload.model_dump(exclude_none=True),
            "created_by": actor.user_id,
        },
        actor.organization_id,
    )
    return StudentResponse(**row)


@router.get("", response_model=list[StudentResponse])
def list_students(
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    return [
        StudentResponse(**row)
        for row in list_tenant_scoped_rows(client, "students", actor.organization_id)
    ]


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: str,
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    row = get_tenant_scoped_row(
        client,
        "students",
        student_id,
        actor.organization_id,
        "Student not found",
    )
    return StudentResponse(**row)
