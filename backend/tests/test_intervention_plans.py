from fastapi.testclient import TestClient

from app.main import app
from app.api import intervention_plans as intervention_plans_api


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, data):
        self._data = data

    def insert(self, payload):
        self._payload = payload
        return self

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
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
            "id": "11111111-1111-1111-1111-111111111111",
            "organization_id": "22222222-2222-2222-2222-222222222222",
            "student_id": "33333333-3333-3333-3333-333333333333",
            "created_by": "44444444-4444-4444-4444-444444444444",
            "title": "Reading Support Plan",
            "status": "draft",
            "summary": "Tier 2 support",
            "priority": "high",
        }
    ])

    monkeypatch.setattr(intervention_plans_api, "get_supabase_admin_client", lambda: fake_client)

    client = TestClient(app)
    response = client.post(
        "/intervention-plans",
        json={
            "organization_id": "22222222-2222-2222-2222-222222222222",
            "student_id": "33333333-3333-3333-3333-333333333333",
            "created_by": "44444444-4444-4444-4444-444444444444",
            "title": "Reading Support Plan",
            "summary": "Tier 2 support",
            "priority": "high",
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Reading Support Plan"
    assert response.json()["priority"] == "high"
    assert fake_client.table_calls[0] == "intervention_plans"


def test_get_intervention_plan_returns_existing_record(monkeypatch):
    fake_client = FakeClient([
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "organization_id": "22222222-2222-2222-2222-222222222222",
            "student_id": "33333333-3333-3333-3333-333333333333",
            "created_by": "44444444-4444-4444-4444-444444444444",
            "title": "Reading Support Plan",
            "status": "active",
            "summary": "Tier 2 support",
            "priority": "high",
        }
    ])

    monkeypatch.setattr(intervention_plans_api, "get_supabase_admin_client", lambda: fake_client)

    client = TestClient(app)
    response = client.get("/intervention-plans/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 200
    assert response.json()["title"] == "Reading Support Plan"
    assert response.json()["status"] == "active"
