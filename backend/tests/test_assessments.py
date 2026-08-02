from fastapi.testclient import TestClient

from app.main import app
from app.api import assessments as assessments_api
from app.models.schemas import AssessmentCreateRequest


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


def test_create_assessment_returns_created_record(monkeypatch):
    fake_client = FakeClient([
        {
            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "organization_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "student_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "created_by": "dddddddd-dddd-dddd-dddd-dddddddddddd",
            "title": "Reading Screen",
            "assessment_type": "curriculum_based",
            "status": "draft",
            "notes": "Initial review",
        }
    ])

    monkeypatch.setattr(assessments_api, "get_supabase_admin_client", lambda: fake_client)

    client = TestClient(app)
    response = client.post(
        "/assessments",
        json={
            "organization_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "student_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "created_by": "dddddddd-dddd-dddd-dddd-dddddddddddd",
            "title": "Reading Screen",
            "assessment_type": "curriculum_based",
            "notes": "Initial review",
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Reading Screen"
    assert response.json()["assessment_type"] == "curriculum_based"
    assert fake_client.table_calls[0] == "assessments"


def test_get_assessment_returns_existing_record(monkeypatch):
    fake_client = FakeClient([
        {
            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "organization_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "student_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "created_by": "dddddddd-dddd-dddd-dddd-dddddddddddd",
            "title": "Reading Screen",
            "assessment_type": "curriculum_based",
            "status": "draft",
            "notes": "Initial review",
        }
    ])

    monkeypatch.setattr(assessments_api, "get_supabase_admin_client", lambda: fake_client)

    client = TestClient(app)
    response = client.get("/assessments/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

    assert response.status_code == 200
    assert response.json()["title"] == "Reading Screen"
    assert response.json()["assessment_type"] == "curriculum_based"


def test_assessment_create_request_model_validates_required_fields():
    payload = AssessmentCreateRequest(
        organization_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        student_id="cccccccc-cccc-cccc-cccc-cccccccccccc",
        created_by="dddddddd-dddd-dddd-dddd-dddddddddddd",
        title="Reading Screen",
        assessment_type="curriculum_based",
    )

    assert payload.title == "Reading Screen"
    assert payload.status == "draft"
