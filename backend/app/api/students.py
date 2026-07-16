from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.supabase_service import get_supabase_admin_client

router = APIRouter(prefix="/students", tags=["students"])


class StudentCreateRequest(BaseModel):
    organization_id: str = Field(..., min_length=1)
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
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreateRequest):
    client = get_supabase_admin_client()
    response = client.table("students").insert(payload.model_dump(exclude_none=True)).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Student could not be created")

    return StudentResponse(**response.data[0])


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: str):
    client = get_supabase_admin_client()
    response = client.table("students").select("*").eq("id", student_id).limit(1).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Student not found")

    return StudentResponse(**response.data[0])
