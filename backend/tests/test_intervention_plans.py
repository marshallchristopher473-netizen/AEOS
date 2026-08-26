from tests.fakes import ORG_A, ORG_B, PLAN_A, PLAN_B, STUDENT_A, STUDENT_B, USER_A


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
