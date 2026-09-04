import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.dependencies import get_current_actor  # noqa: E402
from app.main import app  # noqa: E402
from app.models.schemas import AuthenticatedActor  # noqa: E402
from app.services.supabase_service import get_supabase_admin_client  # noqa: E402
from tests.fakes import ORG_A, USER_A, USER_SUPPORT_A, FakeClient, seeded_tables  # noqa: E402


@pytest.fixture
def actor_a() -> AuthenticatedActor:
    return AuthenticatedActor(
        user_id=USER_A,
        organization_id=ORG_A,
        role="teacher",
        auth_user_id="auth-user-a",
    )


@pytest.fixture
def admin_actor_a() -> AuthenticatedActor:
    return AuthenticatedActor(
        user_id=USER_A,
        organization_id=ORG_A,
        role="admin",
        auth_user_id="auth-user-a",
    )


@pytest.fixture
def support_actor_a() -> AuthenticatedActor:
    return AuthenticatedActor(
        user_id=USER_SUPPORT_A,
        organization_id=ORG_A,
        role="support",
        auth_user_id="auth-support-a",
    )


@pytest.fixture
def fake_db() -> FakeClient:
    return FakeClient(seeded_tables())


@pytest.fixture
def api_client(fake_db: FakeClient, actor_a: AuthenticatedActor):
    app.dependency_overrides[get_current_actor] = lambda: actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(fake_db: FakeClient, admin_actor_a: AuthenticatedActor):
    app.dependency_overrides[get_current_actor] = lambda: admin_actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def support_client(fake_db: FakeClient, support_actor_a: AuthenticatedActor):
    app.dependency_overrides[get_current_actor] = lambda: support_actor_a
    app.dependency_overrides[get_supabase_admin_client] = lambda: fake_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def public_client():
    app.dependency_overrides.clear()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
