from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.supabase_service import get_supabase_admin_client

router = APIRouter(prefix="/intervention-plans", tags=["intervention-plans"])


class InterventionPlanCreateRequest(BaseModel):
    organization_id: str = Field(..., min_length=1)
    student_id: str = Field(..., min_length=1)
    created_by: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    status: str = Field(default="draft", min_length=1)
    priority: str = Field(default="medium", min_length=1)
    summary: Optional[str] = None


class InterventionPlanResponse(BaseModel):
    id: str
    organization_id: str
    student_id: str
    created_by: str
    title: str
    status: str
    priority: str
    summary: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.post("", response_model=InterventionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_intervention_plan(payload: InterventionPlanCreateRequest):
    client = get_supabase_admin_client()
    response = (
        client.table("intervention_plans")
        .insert(payload.model_dump(exclude_none=True))
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=500, detail="Intervention plan could not be created")

    return InterventionPlanResponse(**response.data[0])


@router.get("/student/{student_id}", response_model=List[InterventionPlanResponse])
def get_intervention_plans_for_student(student_id: str):
    client = get_supabase_admin_client()
    response = (
        client.table("intervention_plans")
        .select("*")
        .eq("student_id", student_id)
        .order("created_at", desc=True)
        .execute()
    )

    return [InterventionPlanResponse(**row) for row in response.data]
