from fastapi.testclient import TestClient

from app.core.dependencies import get_current_actor
from app.main import app
from app.services.supabase_service import get_supabase_admin_client


def _seed_student(client, actor, **overrides):
    row = {
        "id": "student-1",
        "organization_id": actor.organization_id,
        "school_id": None,
        "student_number": "STU-1",
        "first_name": "Ava",
        "last_name": "Nguyen",
        "grade_level": "5",
        "iep_status": False,
        "birth_date": None,
        "created_by": actor.user_id,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    row.update(overrides)
    client.seed("students", [row])
    return row


def test_create_student_requires_authentication(fake_client):
    """No Authorization header at all -> 401 (not the FastAPI HTTPBearer
    default of 403), with no dependency override in play so this exercises
    the real chain up to the point HTTPBearer(auto_error=False) hands a
    None credential to get_current_user."""
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).post(
        "/students",
        json={"first_name": "Ava", "last_name": "Nguyen"},
    )

    assert response.status_code == 401
    assert fake_client.rows("students") == []


def test_create_student_rejects_invalid_token_end_to_end(fake_client, monkeypatch):
    """A syntactically-present but invalid bearer token -> 401, exercised
    through the real get_current_user/get_jwks chain (JWKS + jwt.decode
    mocked, matching test_auth.py's pattern) rather than overriding
    get_current_actor - this proves the full route wiring rejects bad
    tokens, not just the isolated dependency function."""
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    from app.core import auth as auth_module
    from jose import JWTError

    async def fake_get_jwks():
        return {"keys": [{"kid": "test-kid", "kty": "RSA", "n": "abc", "e": "AQAB"}]}

    def fake_decode(*_args, **_kwargs):
        raise JWTError("bad signature")

    monkeypatch.setattr(auth_module, "get_jwks", fake_get_jwks)
    monkeypatch.setattr(auth_module.jwt, "get_unverified_header", lambda token: {"kid": "test-kid"})
    monkeypatch.setattr(auth_module.jwt, "decode", fake_decode)

    response = TestClient(app).post(
        "/students",
        json={"first_name": "Ava", "last_name": "Nguyen"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401
    assert fake_client.rows("students") == []


def test_create_student_derives_organization_and_creator_from_actor(fake_client, actor_a):
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).post(
        "/students",
        json={"first_name": "Ava", "last_name": "Nguyen"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["organization_id"] == actor_a.organization_id
    assert body["created_by"] == actor_a.user_id
    stored = fake_client.rows("students")[0]
    assert stored["organization_id"] == actor_a.organization_id
    assert stored["created_by"] == actor_a.user_id


def test_create_student_rejects_spoofed_identity_fields(fake_client, actor_a):
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    spoofable_payloads = [
        {"first_name": "Ava", "last_name": "Nguyen", "organization_id": "attacker-org"},
        {"first_name": "Ava", "last_name": "Nguyen", "organizationId": "attacker-org"},
        {"first_name": "Ava", "last_name": "Nguyen", "created_by": "attacker-user"},
        {"first_name": "Ava", "last_name": "Nguyen", "createdBy": "attacker-user"},
        {"first_name": "Ava", "last_name": "Nguyen", "user_id": "attacker-user"},
        {"first_name": "Ava", "last_name": "Nguyen", "userId": "attacker-user"},
        {"first_name": "Ava", "last_name": "Nguyen", "owner_id": "attacker-user"},
        {"first_name": "Ava", "last_name": "Nguyen", "ownerId": "attacker-user"},
        {"first_name": "Ava", "last_name": "Nguyen", "role": "admin"},
    ]

    client = TestClient(app)
    for payload in spoofable_payloads:
        response = client.post("/students", json=payload)
        assert response.status_code == 422, payload

    assert fake_client.rows("students") == []


def test_create_student_rejects_cross_tenant_school(fake_client, actor_a, actor_b):
    fake_client.seed(
        "schools",
        [{"id": "school-b-1", "organization_id": actor_b.organization_id, "name": "Tenant B School"}],
    )
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).post(
        "/students",
        json={"first_name": "Ava", "last_name": "Nguyen", "school_id": "school-b-1"},
    )

    assert response.status_code == 404
    assert fake_client.rows("students") == []
    # The failure body must not confirm the school exists in another tenant.
    assert "Tenant B" not in response.text
    assert actor_b.organization_id not in response.text


def test_get_student_returns_own_tenant_record(fake_client, actor_a):
    row = _seed_student(fake_client, actor_a)
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).get(f"/students/{row['id']}")

    assert response.status_code == 200
    assert response.json()["first_name"] == "Ava"


def test_get_student_hides_cross_tenant_record(fake_client, actor_a, actor_b):
    row = _seed_student(fake_client, actor_b, id="student-b-1")
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_client

    response = TestClient(app).get(f"/students/{row['id']}")

    assert response.status_code == 404
    # Not 403 - a 403 would confirm the id exists in some other tenant.
    assert "Nguyen" not in response.text
