from typing import Any, Dict, List

from app.models.schemas import AssessmentResponse
from app.services.tenant_scope import (
    get_tenant_scoped_row,
    insert_tenant_scoped_row,
    list_tenant_scoped_rows,
)


class AssessmentService:
    def __init__(self, client):
        self.client = client

    def create_assessment(
        self,
        payload: Dict[str, Any],
        organization_id: str,
    ) -> AssessmentResponse:
        row = insert_tenant_scoped_row(
            self.client,
            "assessments",
            payload,
            organization_id,
        )
        return AssessmentResponse(**row)

    def list_assessments(self, organization_id: str) -> List[AssessmentResponse]:
        return [
            AssessmentResponse(**row)
            for row in list_tenant_scoped_rows(
                self.client,
                "assessments",
                organization_id,
            )
        ]

    def get_assessment(
        self,
        assessment_id: str,
        organization_id: str,
    ) -> AssessmentResponse:
        row = get_tenant_scoped_row(
            self.client,
            "assessments",
            assessment_id,
            organization_id,
            "Assessment not found",
        )
        return AssessmentResponse(**row)
