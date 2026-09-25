import pytest
from fastapi import HTTPException

from app.core.dependencies import get_current_actor, get_db_user
from tests.fakes import ORG_A, ORG_B, USER_A, USER_B, FakeClient, seeded_tables


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
async def test_client_supplied_user_id_claim_cannot_replace_the_resolved_actor():
    """M03: the actor's identity is the database row, never a client-supplied claim.

    `sub` is the only token field with authority. A `user_id` claim naming a
    *real, active* user in another organization is the strongest form of this
    attack: if it were honoured, the attacker would inherit that user's
    identity and tenant, and every downstream tenant filter would then scope
    correctly to the wrong organization.
    """
    payload = {"sub": "auth-user-a", "user_id": USER_B}

    actor = await get_current_actor(
        await get_db_user(payload, FakeClient(seeded_tables()))
    )

    assert actor.user_id == USER_A
    assert actor.organization_id == ORG_A


@pytest.mark.asyncio
async def test_client_supplied_organization_id_claim_cannot_grant_another_tenant():
    """M04: tenant authority comes from the user row, never from a token claim.

    `test_db_user_is_resolved_by_verified_subject_...` spoofs the non-existent
    organization `"spoofed-org"`, so an implementation that trusted the claim
    would fail closed on the organization lookup and still look correct. This
    test spoofs ORG_B, which is a real and *active* organization, so trusting
    the claim produces a working cross-tenant takeover rather than a denial —
    the only version of this mutation that a test can honestly be said to kill.
    """
    payload = {"sub": "auth-user-a", "organization_id": ORG_B}

    actor = await get_current_actor(
        await get_db_user(payload, FakeClient(seeded_tables()))
    )

    assert actor.organization_id == ORG_A
    assert actor.user_id == USER_A


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


@pytest.mark.asyncio
async def test_missing_audience_is_rejected_before_any_actor_or_tenant_query():
    """AC-2.6: rejection must precede actor context and tenant-scoped database work.

    `get_db_user` is the first dependency that touches the database, and it
    depends on `get_current_user`. If `get_current_user` raises, no user row is
    resolved, no organization is looked up, and no tenant-scoped query is ever
    issued. This asserts that ordering by observation — the fake client records
    every query it receives, and the list must be empty.
    """
    import time

    from fastapi.security import HTTPAuthorizationCredentials

    from app.core import auth
    from tests.test_auth import AUDIENCE, ISSUER, OMIT, b64url_uint, make_token

    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private_key.public_key().public_numbers()
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_jwk = {
        "kid": "test-kid",
        "kty": "RSA",
        "alg": "RS256",
        "use": "sig",
        "n": b64url_uint(public_numbers.n),
        "e": b64url_uint(public_numbers.e),
    }

    async def fake_get_jwks(force_refresh=False):
        return {"keys": [public_jwk]}

    original_issuer = auth.SUPABASE_JWT_ISSUER
    original_audience = auth.SUPABASE_JWT_AUDIENCE
    original_get_jwks = auth.get_jwks
    auth.SUPABASE_JWT_ISSUER = ISSUER
    auth.SUPABASE_JWT_AUDIENCE = AUDIENCE
    auth.get_jwks = fake_get_jwks
    try:
        fake_db = FakeClient(seeded_tables())
        token = make_token(private_pem, aud=OMIT)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            payload = await auth.get_current_user(credentials)
            # Unreachable while the audience check holds. Present so that if
            # acceptance were restored, the test fails on the DB assertion
            # below rather than passing for the wrong reason.
            await get_db_user(payload, fake_db)

        assert exc_info.value.status_code == 401
        assert fake_db.queries == [], (
            "a token with no audience claim reached a tenant-scoped query"
        )
    finally:
        auth.SUPABASE_JWT_ISSUER = original_issuer
        auth.SUPABASE_JWT_AUDIENCE = original_audience
        auth.get_jwks = original_get_jwks
