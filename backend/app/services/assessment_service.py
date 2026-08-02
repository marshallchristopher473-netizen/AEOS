from fastapi import HTTPException, status

from app.models.schemas import AssessmentCreateRequest, AssessmentResponse


class AssessmentService:
    def __init__(self, client):
        self.client = client

    def create_assessment(self, payload: AssessmentCreateRequest) -> AssessmentResponse:
        response = self.client.table("assessments").insert(payload.model_dump(exclude_none=True)).execute()

        if not response.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assessment could not be created")

        return AssessmentResponse(**response.data[0])

    def get_assessment(self, assessment_id: str) -> AssessmentResponse:
        response = self.client.table("assessments").select("*").eq("id", assessment_id).limit(1).execute()

        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

        return AssessmentResponse(**response.data[0])
