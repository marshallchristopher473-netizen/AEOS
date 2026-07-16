from fastapi.testclient import TestClient

from app.main import app
from app.api import intervention_plans as intervention_plans_api


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, data):
        self._data = data
        self.last_insert = None

    def insert(self, payload):
        self.last_insert = payload
        return self

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def execute(self):
        return FakeResponse(self._data)


class FakeClient:
    def __init__(self, data):
        self._data = data
        self.table_calls = []

    def table(self, name):
        self.table_calls.append(name)
        return FakeTable(self._data)


def test_create_intervention_plan_returns_created_record(monkeypatch):
    fake_client = FakeClient([
        {
            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "organization_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "student_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "created_by": "dddddddd-dddd-dddd-dddd-dddddddddddd",
            "title": "Reading Support Plan",
            "status": "draft",
            "priority": "high",
            "summary": "Focus on phonics and fluency.",
        }
    ])

    monkeypatch.setattr(intervention_plans_api, "get_supabase_admin_client", lambda: fake_client)

    client = TestClient(app)
    response = client.post(
        "/intervention-plans",
        json={
            "organization_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "student_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "created_by": "dddddddd-dddd-dddd-dddd-dddddddddddd",
            "title": "Reading Support Plan",
            "priority": "high",
            "summary": "Focus on phonics and fluency.",
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Reading Support Plan"
    assert response.json()["priority"] == "high"
    assert response.json()["status"] == "draft"
    assert fake_client.table_calls[0] == "intervention_plans"


def test_create_intervention_plan_uses_default_status_and_priority(monkeypatch):
    fake_client = FakeClient([
        {
            "id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
            "organization_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "student_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "created_by": "dddddddd-dddd-dddd-dddd-dddddddddddd",
            "title": "Math Intervention",
            "status": "draft",
            "priority": "medium",
        }
    ])

    monkeypatch.setattr(intervention_plans_api, "get_supabase_admin_client", lambda: fake_client)

    client = TestClient(app)
    response = client.post(
        "/intervention-plans",
        json={
            "organization_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "student_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "created_by": "dddddddd-dddd-dddd-dddd-dddddddddddd",
            "title": "Math Intervention",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "draft"
    assert response.json()["priority"] == "medium"


def test_get_intervention_plans_for_student_returns_list(monkeypatch):
    fake_client = FakeClient([
        {
            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "organization_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "student_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "created_by": "dddddddd-dddd-dddd-dddd-dddddddddddd",
            "title": "Reading Support Plan",
            "status": "active",
            "priority": "high",
        },
        {
            "id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
            "organization_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "student_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "created_by": "dddddddd-dddd-dddd-dddd-dddddddddddd",
            "title": "Math Intervention",
            "status": "draft",
            "priority": "medium",
        },
    ])

    monkeypatch.setattr(intervention_plans_api, "get_supabase_admin_client", lambda: fake_client)

    client = TestClient(app)
    response = client.get("/intervention-plans/student/cccccccc-cccc-cccc-cccc-cccccccccccc")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Reading Support Plan"
    assert data[1]["title"] == "Math Intervention"
    assert fake_client.table_calls[0] == "intervention_plans"


def test_get_intervention_plans_for_student_returns_empty_list(monkeypatch):
    fake_client = FakeClient([])

    monkeypatch.setattr(intervention_plans_api, "get_supabase_admin_client", lambda: fake_client)

    client = TestClient(app)
    response = client.get("/intervention-plans/student/99999999-9999-9999-9999-999999999999")

    assert response.status_code == 200
    assert response.json() == []
