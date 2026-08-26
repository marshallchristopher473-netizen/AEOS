from fastapi.testclient import TestClient

from app.core.dependencies import get_current_actor
from app.main import app
from app.services.supabase_service import get_supabase_admin_client


def _seed_student(client, actor, student_id="student-1"):
    client.seed(
        "students",
        [
            {
                "id": student_id,
                "organization_id": actor.organization_id,
                "first_name": "Ava",
                "last_name": "Nguyen",
            }
        ],
    )
    return student_id


def _seed_plan(client, actor, **overrides):
    row = {
        "id": "plan-1",
        "organization_id": actor.organization_id,
        "student_id": "student-1",
        "created_by": actor.user_id,
        "title": "Reading Support Plan",
        "status": "active",
        "summary": "Tier 2 support",
        "priority": "high",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    row.update(overrides)
    client.seed("intervention_plans", [row])
    return row


def test_create_intervention_plan_requires_authentication(fake_client):
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).post(
        "/intervention-plans",
        json={"student_id": "student-1", "title": "Reading Support Plan"},
    )

    assert response.status_code == 401
    assert fake_client.rows("intervention_plans") == []


def test_create_intervention_plan_derives_organization_and_creator_from_actor(fake_client, actor_a):
    student_id = _seed_student(fake_client, actor_a)
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).post(
        "/intervention-plans",
        json={"student_id": student_id, "title": "Reading Support Plan", "summary": "Tier 2 support", "priority": "high"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["organization_id"] == actor_a.organization_id
    assert body["created_by"] == actor_a.user_id


def test_create_intervention_plan_rejects_spoofed_identity_fields(fake_client, actor_a):
    student_id = _seed_student(fake_client, actor_a)
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    base = {"student_id": student_id, "title": "Reading Support Plan"}
    spoofable_payloads = [
        {**base, "organization_id": "attacker-org"},
        {**base, "organizationId": "attacker-org"},
        {**base, "created_by": "attacker-user"},
        {**base, "createdBy": "attacker-user"},
        {**base, "user_id": "attacker-user"},
        {**base, "userId": "attacker-user"},
        {**base, "owner_id": "attacker-user"},
        {**base, "ownerId": "attacker-user"},
        {**base, "role": "admin"},
    ]

    client = TestClient(app)
    for payload in spoofable_payloads:
        response = client.post("/intervention-plans", json=payload)
        assert response.status_code == 422, payload

    assert fake_client.rows("intervention_plans") == []


def test_create_intervention_plan_rejects_cross_tenant_student(fake_client, actor_a, actor_b):
    student_id = _seed_student(fake_client, actor_b, student_id="student-b-1")
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).post(
        "/intervention-plans",
        json={"student_id": student_id, "title": "Reading Support Plan"},
    )

    assert response.status_code == 404
    assert fake_client.rows("intervention_plans") == []
    assert actor_b.organization_id not in response.text


def test_get_intervention_plan_returns_own_tenant_record(fake_client, actor_a):
    row = _seed_plan(fake_client, actor_a)
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).get(f"/intervention-plans/{row['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Reading Support Plan"


def test_get_intervention_plan_hides_cross_tenant_record(fake_client, actor_a, actor_b):
    row = _seed_plan(fake_client, actor_b, id="plan-b-1")
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).get(f"/intervention-plans/{row['id']}")

    assert response.status_code == 404
    assert "Reading Support Plan" not in response.text
