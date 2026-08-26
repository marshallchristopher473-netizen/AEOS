from typing import Any, Dict

from app.models.schemas import AssessmentResponse
from app.services.tenant_scope import get_tenant_scoped_row, insert_tenant_scoped_row


class AssessmentService:
    def __init__(self, client):
        self.client = client

    def create_assessment(self, payload: Dict[str, Any]) -> AssessmentResponse:
        """payload must already include a server-derived organization_id
        and created_by - see backend/app/api/assessments.py for where
        those are set from the authenticated actor."""
        row = insert_tenant_scoped_row(self.client, "assessments", payload)
        return AssessmentResponse(**row)

    def get_assessment(self, assessment_id: str, organization_id: str) -> AssessmentResponse:
        row = get_tenant_scoped_row(
            self.client,
            "assessments",
            assessment_id,
            organization_id,
            not_found_detail="Assessment not found",
        )
        return AssessmentResponse(**row)
