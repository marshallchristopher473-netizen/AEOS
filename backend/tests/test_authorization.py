import pytest
from fastapi import HTTPException

from app.core.dependencies import require_privileged_write, require_role
from app.models.schemas import AuthenticatedActor
from tests.fakes import ASSESSMENT_A, ORG_A, STUDENT_A, USER_A


PRIVILEGED_WRITES = (
    ("post", "/students", {"first_name": "A", "last_name": "Student"}),
    (
        "post",
        "/assessments",
        {
            "student_id": STUDENT_A,
            "title": "Screen",
            "assessment_type": "curriculum_based",
        },
    ),
    (
        "post",
        "/intervention-plans",
        {"student_id": STUDENT_A, "title": "Plan"},
    ),
    (
        "post",
        "/assessment-results",
        {"assessment_id": ASSESSMENT_A, "score": 80, "max_score": 100},
    ),
)


@pytest.mark.parametrize(("method", "path", "payload"), PRIVILEGED_WRITES)
def test_support_role_is_forbidden_from_privileged_writes(support_client, method, path, payload):
    response = support_client.request(method, path, json=payload)

    assert response.status_code == 403


@pytest.mark.parametrize(("method", "path", "payload"), PRIVILEGED_WRITES)
def test_teacher_role_is_authorized_for_privileged_writes(api_client, method, path, payload):
    response = api_client.request(method, path, json=payload)

    assert response.status_code == 201


@pytest.mark.parametrize(("method", "path", "payload"), PRIVILEGED_WRITES)
def test_admin_role_is_authorized_for_privileged_writes(admin_client, method, path, payload):
    response = admin_client.request(method, path, json=payload)

    assert response.status_code == 201


def test_support_role_still_has_read_access(support_client):
    response = support_client.get("/students")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_require_role_rejects_role_outside_allow_list():
    actor = AuthenticatedActor(
        user_id=USER_A,
        organization_id=ORG_A,
        role="support",
        auth_user_id="auth-support-a",
    )
    dependency = require_role("teacher", "admin")

    with pytest.raises(HTTPException) as exc_info:
        await dependency(actor)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_require_role_accepts_allow_listed_role():
    actor = AuthenticatedActor(
        user_id=USER_A,
        organization_id=ORG_A,
        role="admin",
        auth_user_id="auth-user-a",
    )

    assert await require_privileged_write(actor) is actor


def test_require_role_requires_at_least_one_allowed_role():
    with pytest.raises(ValueError):
        require_role()
