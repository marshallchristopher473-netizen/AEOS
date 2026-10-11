from pydantic import ValidationError
import pytest
from uuid import UUID

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


def test_review_collection_filters_to_one_assessment(api_client, fake_db):
    other_assessment = "14141414-1414-4414-8414-141414141414"
    fake_db.tables["assessment_results"].append({
        **fake_db.tables["assessment_results"][0],
        "id": "other-result-in-same-tenant",
        "assessment_id": other_assessment,
    })
    response = api_client.get("/assessment-results", params={"assessment_id": ASSESSMENT_A})

    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == [ASSESSMENT_RESULT_A]
    assert fake_db.queries[-1]["filters"] == {"organization_id": ORG_A}


@pytest.mark.parametrize("assessment_id", [ASSESSMENT_B, "missing-assessment"])
def test_review_collection_rejects_inaccessible_assessment(api_client, fake_db, assessment_id):
    response = api_client.get("/assessment-results", params={"assessment_id": assessment_id})

    assert response.status_code == 404
    assert fake_db.queries[-1]["table"] == "assessments"
    assert fake_db.queries[-1]["filters"] == {"id": assessment_id, "organization_id": ORG_A}


def test_review_collection_can_be_empty(api_client, fake_db):
    fake_db.tables["assessment_results"] = []
    response = api_client.get("/assessment-results", params={"assessment_id": ASSESSMENT_A})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("status", ["draft", "complete"])
def test_teacher_creates_assessment_then_saves_and_reloads_review(api_client, fake_db, status):
    assessment = api_client.post("/assessments", json={
        "student_id": STUDENT_A,
        "title": "Synthetic review workflow",
        "assessment_type": "reading",
    })
    assert assessment.status_code == 201
    assessment_id = assessment.json()["id"]
    assert UUID(assessment_id).version == 4
    # The schema has no ID default: the service, not the fake, must supply it.
    assert fake_db.queries[-1]["payload"]["id"] == assessment_id

    saved = api_client.post("/assessment-results", json={
        "assessment_id": assessment_id,
        "score": 0,
        "max_score": 10,
        "summary": "Teacher-entered synthetic findings",
        "status": status,
    })
    assert saved.status_code == 201
    body = saved.json()
    assert UUID(body["id"]).version == 4
    assert fake_db.queries[-1]["payload"]["id"] == body["id"]
    assert body["organization_id"] == ORG_A
    assert body["created_by"] == USER_A
    assert body["student_id"] == STUDENT_A
    assert body["score"] == 0
    assert body["status"] == status

    reloaded = api_client.get("/assessment-results", params={"assessment_id": assessment_id})
    assert reloaded.status_code == 200
    assert reloaded.json() == [body]
    assert api_client.get(f"/assessments/{assessment_id}").json()["status"] == "draft"


@pytest.mark.parametrize("fields", [
    {"score": -1}, {"max_score": 0}, {"max_score": 0.001},
    {"score": 101, "max_score": 100}, {"score": 10000},
    {"max_score": 10000}, {"status": "unsupported"},
])
def test_invalid_review_is_rejected_before_insert(api_client, fake_db, fields):
    response = api_client.post("/assessment-results", json={**valid_payload(), **fields})
    assert response.status_code == 422
    assert not any(query["operation"] == "insert" for query in fake_db.queries)


@pytest.mark.parametrize("score", [float("inf"), float("nan")])
def test_nonfinite_review_scores_are_rejected(score):
    with pytest.raises(ValidationError):
        AssessmentResultCreateRequest(**{**valid_payload(), "score": score})


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
