from pydantic import ValidationError
import pytest

from app.models.schemas import AssessmentResultCreateRequest
from tests.fakes import (
    ASSESSMENT_A,
    ASSESSMENT_B,
    ASSESSMENT_RESULT_A,
    ASSESSMENT_RESULT_B,
    ORG_A,
    ORG_B,
    STUDENT_A,
    USER_A,
)


def valid_payload():
    return {
        "assessment_id": ASSESSMENT_A,
        "score": 88,
        "max_score": 100,
        "summary": "Synthetic fixture",
    }


def test_assessment_result_collection_is_tenant_scoped(api_client, fake_db):
    response = api_client.get("/assessment-results")

    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == [ASSESSMENT_RESULT_A]
    assert fake_db.queries[-1]["filters"] == {"organization_id": ORG_A}


def test_same_tenant_assessment_result_object_is_returned(api_client):
    response = api_client.get(f"/assessment-results/{ASSESSMENT_RESULT_A}")

    assert response.status_code == 200
    assert response.json()["id"] == ASSESSMENT_RESULT_A


def test_cross_tenant_assessment_result_object_is_404(api_client, fake_db):
    response = api_client.get(f"/assessment-results/{ASSESSMENT_RESULT_B}")

    assert response.status_code == 404
    assert fake_db.queries[-1]["filters"] == {
        "id": ASSESSMENT_RESULT_B,
        "organization_id": ORG_A,
    }


def test_assessment_result_create_derives_tenant_actor_and_student_server_side(
    api_client, fake_db
):
    response = api_client.post("/assessment-results", json=valid_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["organization_id"] == ORG_A
    assert body["created_by"] == USER_A
    assert body["student_id"] == STUDENT_A
    inserted = fake_db.queries[-1]["payload"]
    assert inserted["organization_id"] == ORG_A
    assert inserted["created_by"] == USER_A
    assert inserted["student_id"] == STUDENT_A


def test_assessment_result_create_rejects_cross_tenant_assessment_id(api_client, fake_db):
    payload = valid_payload()
    payload["assessment_id"] = ASSESSMENT_B

    response = api_client.post("/assessment-results", json=payload)

    assert response.status_code == 404
    assert fake_db.queries[-1]["filters"] == {
        "id": ASSESSMENT_B,
        "organization_id": ORG_A,
    }


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("id", "attacker-controlled-result"),
        ("organization_id", ORG_B),
        ("created_by", "attacker"),
        ("student_id", "attacker-controlled-student"),
    ),
)
def test_assessment_result_create_rejects_each_spoofed_identity_field(
    api_client,
    field,
    value,
):
    response = api_client.post(
        "/assessment-results",
        json={**valid_payload(), field: value},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("id", "attacker-controlled-result"),
        ("organization_id", ORG_B),
        ("created_by", "attacker"),
        ("student_id", "attacker-controlled-student"),
    ),
)
def test_assessment_result_request_schema_rejects_each_identity_field(field, value):
    with pytest.raises(ValidationError):
        AssessmentResultCreateRequest(
            **valid_payload(),
            **{field: value},
        )
