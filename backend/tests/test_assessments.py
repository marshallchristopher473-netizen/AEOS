from fastapi.testclient import TestClient

from app.core.dependencies import get_current_actor
from app.main import app
from app.models.schemas import AssessmentCreateRequest
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


def _seed_assessment(client, actor, **overrides):
    row = {
        "id": "assessment-1",
        "organization_id": actor.organization_id,
        "student_id": "student-1",
        "created_by": actor.user_id,
        "title": "Reading Screen",
        "assessment_type": "curriculum_based",
        "status": "draft",
        "notes": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    row.update(overrides)
    client.seed("assessments", [row])
    return row


def test_create_assessment_requires_authentication(fake_client):
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).post(
        "/assessments",
        json={"student_id": "student-1", "title": "Reading Screen", "assessment_type": "curriculum_based"},
    )

    assert response.status_code == 401
    assert fake_client.rows("assessments") == []


def test_create_assessment_derives_organization_and_creator_from_actor(fake_client, actor_a):
    student_id = _seed_student(fake_client, actor_a)
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).post(
        "/assessments",
        json={"student_id": student_id, "title": "Reading Screen", "assessment_type": "curriculum_based"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["organization_id"] == actor_a.organization_id
    assert body["created_by"] == actor_a.user_id


def test_create_assessment_rejects_spoofed_identity_fields(fake_client, actor_a):
    student_id = _seed_student(fake_client, actor_a)
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    base = {"student_id": student_id, "title": "Reading Screen", "assessment_type": "curriculum_based"}
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
        response = client.post("/assessments", json=payload)
        assert response.status_code == 422, payload

    assert fake_client.rows("assessments") == []


def test_create_assessment_rejects_cross_tenant_student(fake_client, actor_a, actor_b):
    student_id = _seed_student(fake_client, actor_b, student_id="student-b-1")
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).post(
        "/assessments",
        json={"student_id": student_id, "title": "Reading Screen", "assessment_type": "curriculum_based"},
    )

    assert response.status_code == 404
    assert fake_client.rows("assessments") == []
    assert actor_b.organization_id not in response.text


def test_get_assessment_returns_own_tenant_record(fake_client, actor_a):
    row = _seed_assessment(fake_client, actor_a)
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).get(f"/assessments/{row['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Reading Screen"


def test_get_assessment_hides_cross_tenant_record(fake_client, actor_a, actor_b):
    row = _seed_assessment(fake_client, actor_b, id="assessment-b-1")
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).get(f"/assessments/{row['id']}")

    assert response.status_code == 404
    assert "Reading Screen" not in response.text


def test_assessment_create_request_model_validates_required_fields():
    payload = AssessmentCreateRequest(
        student_id="student-1",
        title="Reading Screen",
        assessment_type="curriculum_based",
    )

    assert payload.title == "Reading Screen"
    assert payload.status == "draft"
