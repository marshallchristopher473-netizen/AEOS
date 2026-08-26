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
)

router = APIRouter(prefix="/intervention-plans", tags=["intervention-plans"])


class InterventionPlanCreateRequest(BaseModel):
    """organization_id and created_by are intentionally absent: they are
    derived server-side from the authenticated actor
    (see app.core.dependencies.get_current_actor), never accepted from the
    client. extra="forbid" rejects a client that still sends them (or any
    other unrecognized field) with a 422, rather than silently ignoring
    the value."""

    model_config = ConfigDict(extra="forbid")

    student_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    status: str = Field(default="draft", min_length=1)
    summary: Optional[str] = None
    priority: str = Field(default="medium", min_length=1)


class InterventionPlanResponse(BaseModel):
    id: str
    organization_id: str
    student_id: str
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
    actor: AuthenticatedActor = Depends(get_current_actor),
    client=Depends(get_supabase_admin_client),
):
    # The referenced student must belong to the actor's own organization -
    # otherwise this would let one tenant attach an intervention plan to
    # another tenant's student. 404 (not 403/400) so a cross-tenant id
    # doesn't confirm its own existence.
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

    row = insert_tenant_scoped_row(client, "intervention_plans", record)
    return InterventionPlanResponse(**row)


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
        not_found_detail="Intervention plan not found",
    )
    return InterventionPlanResponse(**row)
