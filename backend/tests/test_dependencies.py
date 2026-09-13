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

    # Assert on the specific queries rather than whichever ran last, so that
    # adding a resolution step cannot silently invalidate these assertions.
    users_query = next(q for q in fake_db.queries if q["table"] == "users")
    assert users_query["filters"] == {
        "auth_user_id": "auth-user-a",
        "status": "active",
    }

    organization_query = next(
        q for q in fake_db.queries if q["table"] == "organizations"
    )
    assert organization_query["filters"] == {"id": ORG_A, "status": "active"}


@pytest.mark.asyncio
async def test_unknown_subject_is_forbidden():
    fake_db = FakeClient(seeded_tables())

    with pytest.raises(HTTPException) as exc_info:
        await get_db_user({"sub": "unknown-user"}, fake_db)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_suspended_organization_is_forbidden():
    """M1: suspending an organization must remove access immediately.

    `organizations.status` is a modelled lifecycle control. If it is not
    consulted during actor resolution, suspending a district (offboarding,
    non-payment, breach containment) provides no containment at all.
    """
    tables = seeded_tables()
    for organization in tables["organizations"]:
        if organization["id"] == ORG_A:
            organization["status"] = "suspended"

    with pytest.raises(HTTPException) as exc_info:
        await get_db_user({"sub": "auth-user-a"}, FakeClient(tables))

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_missing_organization_fails_closed():
    """An actor whose organization row does not exist must not be resolved."""
    tables = seeded_tables()
    tables["organizations"] = [
        organization
        for organization in tables["organizations"]
        if organization["id"] != ORG_A
    ]

    with pytest.raises(HTTPException) as exc_info:
        await get_db_user({"sub": "auth-user-a"}, FakeClient(tables))

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_disabled_user_is_forbidden():
    """Behavioural counterpart to the query-shape assertion above: seed an
    actually-disabled user and confirm the request fails closed."""
    tables = seeded_tables()
    for user in tables["users"]:
        if user["id"] == USER_A:
            user["status"] = "disabled"

    with pytest.raises(HTTPException) as exc_info:
        await get_db_user({"sub": "auth-user-a"}, FakeClient(tables))

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_active_organization_still_resolves():
    """Positive control: the suspension check must not deny healthy actors."""
    actor = await get_current_actor(
        await get_db_user({"sub": "auth-user-a"}, FakeClient(seeded_tables()))
    )

    assert actor.organization_id == ORG_A
    assert actor.role == "teacher"


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
