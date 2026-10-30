"""Student audit rows against the real schema.

The in-memory fake cannot check what PostgreSQL enforces on audit_logs: the
UUID entity_id, the performed_by foreign key to users, and the id default from
migration 009. These tests run the real student routes through the
service-role adapter from test_create_persists_real_db.py.

Synthetic rows only, in that module's scratch database.
"""

import pytest
from fastapi import HTTPException

from app.api.students import StudentCreateRequest, create_student, get_student
from tests.test_create_persists_real_db import (  # noqa: F401 - fixtures are used by name
    DATABASE_URL,
    ORG_A,
    TEACHER_A,
    USER_A,
    admin_db,
    fresh_database,
    real_client,
)
from tests.test_rls_enforcement import STUDENT_B

pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="AEOS_TEST_DATABASE_URL is not set; real-database audit tests require PostgreSQL",
)


def stored_audit_rows(admin_db, entity_id):
    return admin_db.execute(
        "SELECT entity_type, action, performed_by::text, organization_id::text "
        "FROM public.audit_logs WHERE entity_id = %s ORDER BY action",
        (entity_id,),
    ).fetchall()


def test_student_create_and_view_each_persist_one_audit_row(real_client, admin_db):
    created = create_student(
        StudentCreateRequest(first_name="Audited", last_name="Synthetic"),
        TEACHER_A,
        real_client,
    )
    viewed = get_student(created.id, TEACHER_A, real_client)

    assert viewed.id == created.id
    assert stored_audit_rows(admin_db, created.id) == [
        ("student", "student.create", USER_A, ORG_A),
        ("student", "student.view", USER_A, ORG_A),
    ]


def test_cross_tenant_student_view_persists_no_audit_row(real_client, admin_db):
    with pytest.raises(HTTPException) as refused:
        get_student(STUDENT_B, TEACHER_A, real_client)

    assert refused.value.status_code == 404
    assert stored_audit_rows(admin_db, STUDENT_B) == []
