from tests.fakes import (
    ASSESSMENT_A,
    ASSESSMENT_B,
    ORG_A,
    ORG_B,
    PLAN_A,
    PLAN_B,
    STUDENT_A,
    STUDENT_B,
    USER_A,
)


def valid_payload():
    return {
        "student_id": STUDENT_A,
        "title": "Reading Support Plan",
        "summary": "Synthetic Tier 2 support",
        "priority": "high",
    }


def test_intervention_collection_is_tenant_scoped(api_client, fake_db):
    response = api_client.get("/intervention-plans")

    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == [PLAN_A]
    assert fake_db.queries[-1]["filters"] == {"organization_id": ORG_A}


def test_same_tenant_intervention_object_is_returned(api_client):
    response = api_client.get(f"/intervention-plans/{PLAN_A}")

    assert response.status_code == 200
    assert response.json()["id"] == PLAN_A


def test_cross_tenant_intervention_object_is_404(api_client, fake_db):
    response = api_client.get(f"/intervention-plans/{PLAN_B}")

    assert response.status_code == 404
    assert fake_db.queries[-1]["filters"] == {
        "id": PLAN_B,
        "organization_id": ORG_A,
    }


def test_intervention_create_derives_tenant_and_actor_server_side(api_client, fake_db):
    response = api_client.post("/intervention-plans", json=valid_payload())

    assert response.status_code == 201
    assert response.json()["organization_id"] == ORG_A
    assert response.json()["created_by"] == USER_A
    inserted = fake_db.queries[-1]["payload"]
    assert inserted["organization_id"] == ORG_A
    assert inserted["created_by"] == USER_A


def test_intervention_create_rejects_cross_tenant_student_id(api_client, fake_db):
    payload = valid_payload()
    payload["student_id"] = STUDENT_B

    response = api_client.post("/intervention-plans", json=payload)

    assert response.status_code == 404
    assert fake_db.queries[-1]["filters"] == {
        "id": STUDENT_B,
        "organization_id": ORG_A,
    }


def test_intervention_create_rejects_spoofed_authority_fields(api_client):
    response = api_client.post(
        "/intervention-plans",
        json={**valid_payload(), "organization_id": ORG_B, "created_by": "attacker"},
    )

    assert response.status_code == 422


def test_intervention_create_accepts_same_student_assessment(api_client, fake_db):
    payload = valid_payload()
    payload["assessment_id"] = ASSESSMENT_A

    response = api_client.post("/intervention-plans", json=payload)

    assert response.status_code == 201
    assert response.json()["assessment_id"] == ASSESSMENT_A


def test_intervention_create_rejects_cross_tenant_assessment_id(api_client, fake_db):
    payload = valid_payload()
    payload["assessment_id"] = ASSESSMENT_B

    response = api_client.post("/intervention-plans", json=payload)

    assert response.status_code == 404


def test_intervention_create_rejects_assessment_for_a_different_student(api_client, fake_db):
    other_student_assessment = {
        "id": "44444444-4444-4444-8444-000000000099",
        "organization_id": ORG_A,
        "student_id": STUDENT_B,
        "created_by": USER_A,
        "title": "Mismatched student assessment",
        "assessment_type": "curriculum_based",
        "status": "draft",
    }
    # Same organization as the actor, but the wrong student — this is the
    # attack this relationship check exists to reject: an assessment that is
    # in-tenant but does not belong to the student named on the plan.
    other_student_assessment["organization_id"] = ORG_A
    fake_db.tables["assessments"].append(other_student_assessment)

    payload = valid_payload()
    payload["assessment_id"] = other_student_assessment["id"]

    response = api_client.post("/intervention-plans", json=payload)

    assert response.status_code == 404
