"""Audit trail for student records.

Student create and student view each write one audit_logs row whose tenant and
actor come from the server-derived actor. AI draft decisions are audited by the
database trigger `ai_feedback_decisions_audit` (migration 006) in the same
transaction as the decision; that path is exercised against PostgreSQL in
tests/test_ai_feedback_rls.py.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_actor
from app.main import app
from app.services.supabase_service import get_supabase_admin_client
from tests.fakes import ORG_A, SCHOOL_B, STUDENT_A, STUDENT_B, USER_A, FakeClient, seeded_tables

AUDITED_FIELDS = ("entity_type", "entity_id", "action", "performed_by", "organization_id")


def audit_rows(fake_db):
    return [
        {field: row.get(field) for field in AUDITED_FIELDS}
        for row in fake_db.tables.get("audit_logs", [])
    ]


def test_student_create_writes_one_audit_row_from_the_server_derived_actor(api_client, fake_db):
    response = api_client.post("/students", json={"first_name": "Cara", "last_name": "Gamma"})

    assert response.status_code == 201
    assert audit_rows(fake_db) == [
        {
            "entity_type": "student",
            "entity_id": response.json()["id"],
            "action": "student.create",
            "performed_by": USER_A,
            "organization_id": ORG_A,
        }
    ]


def test_student_view_writes_one_audit_row_from_the_server_derived_actor(api_client, fake_db):
    response = api_client.get(f"/students/{STUDENT_A}")

    assert response.status_code == 200
    assert audit_rows(fake_db) == [
        {
            "entity_type": "student",
            "entity_id": STUDENT_A,
            "action": "student.view",
            "performed_by": USER_A,
            "organization_id": ORG_A,
        }
    ]


def test_cross_tenant_student_view_writes_no_audit_row(api_client, fake_db):
    response = api_client.get(f"/students/{STUDENT_B}")

    assert response.status_code == 404
    assert audit_rows(fake_db) == []


def test_cross_tenant_school_on_create_writes_no_student_and_no_audit_row(api_client, fake_db):
    students_before = len(fake_db.tables["students"])

    response = api_client.post(
        "/students",
        json={"school_id": SCHOOL_B, "first_name": "Cara", "last_name": "Gamma"},
    )

    assert response.status_code == 404
    assert len(fake_db.tables["students"]) == students_before
    assert audit_rows(fake_db) == []


class AuditOutageClient(FakeClient):
    """Every table works except audit_logs, whose writes fail."""

    def table(self, name):
        query = super().table(name)
        if name == "audit_logs":
            def fail():
                raise RuntimeError("synthetic audit outage")

            query.execute = fail
        return query


@pytest.fixture
def audit_outage_client(actor_a):
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: AuditOutageClient(seeded_tables())
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_student_view_fails_closed_when_the_audit_row_cannot_be_written(audit_outage_client):
    response = audit_outage_client.get(f"/students/{STUDENT_A}")

    assert response.status_code == 500
    # No student data leaves the API without its audit row.
    assert response.json() == {"detail": "Audit log could not be written"}


def test_student_create_reports_failure_when_the_audit_row_cannot_be_written(audit_outage_client):
    response = audit_outage_client.post("/students", json={"first_name": "Cara", "last_name": "Gamma"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Audit log could not be written"}
