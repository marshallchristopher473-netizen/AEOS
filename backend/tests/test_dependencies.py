import pytest
from fastapi import HTTPException

from app.core import dependencies


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, data):
        self._data = data
        self.last_eq_column = None
        self.last_eq_value = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, column, value):
        self.last_eq_column = column
        self.last_eq_value = value
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


ACTIVE_USER_ROW = {
    "id": "11111111-1111-1111-1111-111111111111",
    "organization_id": "22222222-2222-2222-2222-222222222222",
    "auth_user_id": "auth-sub-abc",
    "email": "teacher@example.com",
    "full_name": "Ava Johnson",
    "role": "teacher",
    "status": "active",
}


@pytest.mark.asyncio
async def test_get_current_actor_returns_trusted_actor_from_db_record(monkeypatch):
    fake_client = FakeClient([ACTIVE_USER_ROW])
    monkeypatch.setattr(dependencies, "get_supabase_admin_client", lambda: fake_client)

    actor = await dependencies.get_current_actor(user_payload={"sub": "auth-sub-abc"})

    # organization_id, user_id, and role must come from the database row,
    # not from the JWT payload or request data.
    assert actor.user_id == ACTIVE_USER_ROW["id"]
    assert actor.organization_id == ACTIVE_USER_ROW["organization_id"]
    assert actor.role == ACTIVE_USER_ROW["role"]
    assert actor.auth_user_id == "auth-sub-abc"
    assert fake_client.table_calls == ["users"]


@pytest.mark.asyncio
async def test_get_current_actor_queries_by_auth_user_id_not_email(monkeypatch):
    fake_table_holder = {}

    class TrackingFakeClient(FakeClient):
        def table(self, name):
            table = super().table(name)
            fake_table_holder["table"] = table
            return table

    fake_client = TrackingFakeClient([ACTIVE_USER_ROW])
    monkeypatch.setattr(dependencies, "get_supabase_admin_client", lambda: fake_client)

    await dependencies.get_current_actor(user_payload={"sub": "auth-sub-abc", "email": "someone-else@example.com"})

    assert fake_table_holder["table"].last_eq_column == "auth_user_id"
    assert fake_table_holder["table"].last_eq_value == "auth-sub-abc"


@pytest.mark.asyncio
async def test_get_current_actor_rejects_missing_subject(monkeypatch):
    fake_client = FakeClient([ACTIVE_USER_ROW])
    monkeypatch.setattr(dependencies, "get_supabase_admin_client", lambda: fake_client)

    with pytest.raises(HTTPException) as exc_info:
        await dependencies.get_current_actor(user_payload={})

    assert exc_info.value.status_code == 401
    assert fake_client.table_calls == []


@pytest.mark.asyncio
async def test_get_current_actor_rejects_non_string_subject(monkeypatch):
    fake_client = FakeClient([ACTIVE_USER_ROW])
    monkeypatch.setattr(dependencies, "get_supabase_admin_client", lambda: fake_client)

    with pytest.raises(HTTPException) as exc_info:
        await dependencies.get_current_actor(user_payload={"sub": 12345})

    assert exc_info.value.status_code == 401
    assert fake_client.table_calls == []


@pytest.mark.asyncio
async def test_get_current_actor_rejects_unknown_aeos_user(monkeypatch):
    fake_client = FakeClient([])
    monkeypatch.setattr(dependencies, "get_supabase_admin_client", lambda: fake_client)

    with pytest.raises(HTTPException) as exc_info:
        await dependencies.get_current_actor(user_payload={"sub": "no-such-subject"})

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_actor_rejects_ambiguous_aeos_user(monkeypatch):
    duplicate_row = dict(ACTIVE_USER_ROW, id="33333333-3333-3333-3333-333333333333")
    fake_client = FakeClient([ACTIVE_USER_ROW, duplicate_row])
    monkeypatch.setattr(dependencies, "get_supabase_admin_client", lambda: fake_client)

    with pytest.raises(HTTPException) as exc_info:
        await dependencies.get_current_actor(user_payload={"sub": "auth-sub-abc"})

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_actor_rejects_inactive_user(monkeypatch):
    disabled_row = dict(ACTIVE_USER_ROW, status="disabled")
    fake_client = FakeClient([disabled_row])
    monkeypatch.setattr(dependencies, "get_supabase_admin_client", lambda: fake_client)

    with pytest.raises(HTTPException) as exc_info:
        await dependencies.get_current_actor(user_payload={"sub": "auth-sub-abc"})

    assert exc_info.value.status_code == 403
