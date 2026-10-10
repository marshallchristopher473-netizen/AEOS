from typing import Any, Dict, List

from app.models.schemas import AssessmentResultResponse
from app.services.tenant_scope import (
    assert_related_row_in_tenant,
    get_tenant_scoped_row,
    insert_tenant_scoped_row,
    list_tenant_scoped_rows,
)


class AssessmentResultService:
    def __init__(self, client):
        self.client = client

    def create_assessment_result(
        self,
        payload: Dict[str, Any],
        organization_id: str,
    ) -> AssessmentResultResponse:
        assessment_id = payload["assessment_id"]
        related_assessment = assert_related_row_in_tenant(
            self.client,
            "assessments",
            assessment_id,
            organization_id,
            "Assessment not found",
        )
        row = insert_tenant_scoped_row(
            self.client,
            "assessment_results",
            {
                **payload,
                "student_id": related_assessment["student_id"],
            },
            organization_id,
        )
        return AssessmentResultResponse(**row)

    def list_assessment_results(
        self, organization_id: str, assessment_id: str | None = None
    ) -> List[AssessmentResultResponse]:
        if assessment_id is not None:
            assert_related_row_in_tenant(
                self.client,
                "assessments",
                assessment_id,
                organization_id,
                "Assessment not found",
            )
        return [
            AssessmentResultResponse(**row)
            for row in list_tenant_scoped_rows(
                self.client,
                "assessment_results",
                organization_id,
            )
            if assessment_id is None or row["assessment_id"] == assessment_id
        ]

    def get_assessment_result(
        self,
        assessment_result_id: str,
        organization_id: str,
    ) -> AssessmentResultResponse:
        row = get_tenant_scoped_row(
            self.client,
            "assessment_results",
            assessment_result_id,
            organization_id,
            "Assessment result not found",
        )
        return AssessmentResultResponse(**row)
