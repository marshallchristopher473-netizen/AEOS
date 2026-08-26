import pytest
from fastapi import HTTPException

from app.core.dependencies import get_current_actor, get_db_user
from tests.fakes import ORG_A, USER_A, FakeClient, seeded_tables


@pytest.mark.asyncio
async def test_db_user_is_resolved_by_verified_subject_not_email_or_jwt_authority_fields():
    fake_db = FakeClient(seeded_tables())
    payload = {
        "sub": "auth-user-a",
        "email": "attacker-controlled@example.test",
        "organization_id": "spoofed-org",
        "role": "admin",
    }

    row = await get_db_user(payload, fake_db)
    actor = await get_current_actor(row)

    assert actor.user_id == USER_A
    assert actor.organization_id == ORG_A
    assert actor.role == "teacher"
    assert fake_db.queries[-1]["filters"] == {
        "auth_user_id": "auth-user-a",
        "status": "active",
    }


@pytest.mark.asyncio
async def test_unknown_subject_is_forbidden():
    fake_db = FakeClient(seeded_tables())

    with pytest.raises(HTTPException) as exc_info:
        await get_db_user({"sub": "unknown-user"}, fake_db)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_duplicate_subject_mapping_fails_closed():
    tables = seeded_tables()
    duplicate = dict(tables["users"][0])
    duplicate["id"] = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
    duplicate["organization_id"] = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
    tables["users"].append(duplicate)

    with pytest.raises(HTTPException) as exc_info:
        await get_db_user({"sub": "auth-user-a"}, FakeClient(tables))

    assert exc_info.value.status_code == 403
