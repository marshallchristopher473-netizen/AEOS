import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(autouse=True)
def _clear_dependency_overrides():
    """FastAPI's `app` is a module-level singleton, so a test that
    overrides get_current_actor (or any other dependency) via
    app.dependency_overrides must not leak that override into the next
    test. Runs after every test regardless of which test file it's in."""
    yield
    from app.main import app

    app.dependency_overrides.clear()


@pytest.fixture
def actor_a():
    from app.models.schemas import AuthenticatedActor

    return AuthenticatedActor(
        user_id="user-a-1111-1111-1111-111111111111",
        organization_id="org-a-1111-1111-1111-111111111111",
        role="teacher",
        auth_user_id="auth-a-sub",
    )


@pytest.fixture
def actor_b():
    from app.models.schemas import AuthenticatedActor

    return AuthenticatedActor(
        user_id="user-b-2222-2222-2222-222222222222",
        organization_id="org-b-2222-2222-2222-222222222222",
        role="teacher",
        auth_user_id="auth-b-sub",
    )


@pytest.fixture
def fake_client():
    from fakes import FakeSupabaseClient

    return FakeSupabaseClient()
