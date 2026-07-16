from fastapi.testclient import TestClient

from app.main import app
from app.api import students as students_api


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, data):
        self._data = data
        self.last_insert = None
        self.last_select = None

    def insert(self, payload):
        self.last_insert = payload
        return self

    def select(self, *_args, **_kwargs):
        self.last_select = "select"
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


def test_create_student_returns_created_record(monkeypatch):
    fake_client = FakeClient([
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "organization_id": "22222222-2222-2222-2222-222222222222",
            "first_name": "Ava",
            "last_name": "Nguyen",
            "iep_status": False,
        }
    ])

    monkeypatch.setattr(students_api, "get_supabase_admin_client", lambda: fake_client)

    client = TestClient(app)
    response = client.post(
        "/students",
        json={
            "organization_id": "22222222-2222-2222-2222-222222222222",
            "first_name": "Ava",
            "last_name": "Nguyen",
        },
    )

    assert response.status_code == 201
    assert response.json()["first_name"] == "Ava"
    assert response.json()["last_name"] == "Nguyen"
    assert fake_client.table_calls[0] == "students"


def test_get_student_returns_existing_record(monkeypatch):
    fake_client = FakeClient([
        {
            "id": "33333333-3333-3333-3333-333333333333",
            "organization_id": "44444444-4444-4444-4444-444444444444",
            "first_name": "Liam",
            "last_name": "Chen",
            "iep_status": True,
        }
    ])

    monkeypatch.setattr(students_api, "get_supabase_admin_client", lambda: fake_client)

    client = TestClient(app)
    response = client.get("/students/33333333-3333-3333-3333-333333333333")

    assert response.status_code == 200
    assert response.json()["first_name"] == "Liam"
    assert response.json()["last_name"] == "Chen"
