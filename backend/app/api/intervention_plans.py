from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.core.dependencies import get_current_actor, require_privileged_write
from app.models.schemas import AuthenticatedActor
from app.services.supabase_service import get_supabase_admin_client
from app.services.tenant_scope import (
    assert_related_row_in_tenant,
    get_tenant_scoped_row,
    insert_tenant_scoped_row,
    list_tenant_scoped_rows,
)

router = APIRouter(prefix="/intervention-plans", tags=["intervention-plans"])


class InterventionPlanCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: str = Field(..., min_length=1)
    assessment_id: Optional[str] = None
    title: str = Field(..., min_length=1)
    status: str = Field(default="draft", min_length=1)
    summary: Optional[str] = None
    priority: str = Field(default="medium", min_length=1)


class InterventionPlanResponse(BaseModel):
    id: str
    organization_id: str
    student_id: str
    assessment_id: Optional[str] = None
    created_by: str
    title: str
    status: str
    summary: Optional[str] = None
    priority: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.post("", response_model=InterventionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_intervention_plan(
    payload: InterventionPlanCreateRequest,
    actor: AuthenticatedActor = Depends(require_privileged_write),
    client=Depends(get_supabase_admin_client),
):
    assert_related_row_in_tenant(
        client,
        "students",
        payload.student_id,
        actor.organization_id,
        "Student not found",
    )
    if payload.assessment_id:
        related_assessment = assert_related_row_in_tenant(
            client,
            "assessments",
            payload.assessment_id,
            actor.organization_id,
            "Assessment not found",
        )
        if related_assessment.get("student_id") != payload.student_id:
            raise HTTPException(status_code=404, detail="Assessment not found")

    row = insert_tenant_scoped_row(
        client,
        "intervention_plans",
        {
            **payload.model_dump(exclude_none=True),
            "created_by": actor.user_id,
        },
        actor.organization_id,
    )
    return InterventionPlanResponse(**row)


@router.get("", response_model=list[InterventionPlanResponse])
def list_intervention_plans(
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    return [
        InterventionPlanResponse(**row)
        for row in list_tenant_scoped_rows(
            client,
            "intervention_plans",
            actor.organization_id,
        )
    ]


@router.get("/{plan_id}", response_model=InterventionPlanResponse)
def get_intervention_plan(
    plan_id: str,
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    row = get_tenant_scoped_row(
        client,
        "intervention_plans",
        plan_id,
        actor.organization_id,
        "Intervention plan not found",
    )
    return InterventionPlanResponse(**row)
