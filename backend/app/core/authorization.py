"""Shared role-authorization helper.

No route in this codebase currently restricts an action to specific AEOS
roles (teacher/admin/support) - there is no existing product decision
recorded anywhere about which roles may perform which action. This helper
exists so that if/when such a restriction is added, every route uses the
same check rather than duplicating ad hoc role comparisons. Do not use it
to invent a role restriction that isn't already a recorded product
requirement.
"""
from typing import Iterable

from fastapi import HTTPException, status

from app.models.schemas import AuthenticatedActor


def require_role(actor: AuthenticatedActor, allowed_roles: Iterable[str]) -> None:
    """Raise 403 if actor.role is not one of allowed_roles."""
    if actor.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires a different role",
        )
