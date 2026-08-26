"""Unit tests for the shared role-authorization helper.

No route in this codebase currently gates an action by role (see
app/core/authorization.py's docstring), so there is nothing to test at
the route level for P0-C07 yet. These tests cover the helper directly so
it's proven correct and ready for the first route that needs it, without
inventing a role restriction that isn't an actual product requirement.
"""
import pytest
from fastapi import HTTPException

from app.core.authorization import require_role
from app.models.schemas import AuthenticatedActor


def _actor(role: str) -> AuthenticatedActor:
    return AuthenticatedActor(
        user_id="user-1",
        organization_id="org-1",
        role=role,
        auth_user_id="auth-1",
    )


def test_require_role_allows_matching_role():
    require_role(_actor("admin"), {"admin", "teacher"})  # must not raise


def test_require_role_rejects_non_matching_role():
    with pytest.raises(HTTPException) as exc_info:
        require_role(_actor("support"), {"admin", "teacher"})

    assert exc_info.value.status_code == 403
