from fastapi import Depends, HTTPException, status
from pydantic import ValidationError

from app.core.auth import get_current_user
from app.models.schemas import AuthenticatedActor
from app.services.supabase_service import get_supabase_admin_client


async def get_db_user(
    user_payload: dict = Depends(get_current_user),
    client=Depends(get_supabase_admin_client),
):
    """Resolve the verified JWT subject to exactly one active AEOS user row."""
    auth_user_id = user_payload.get("sub")
    if not isinstance(auth_user_id, str) or not auth_user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT is missing a usable subject",
        )

    response = (
        client.table("users")
        .select("id,organization_id,auth_user_id,role,status")
        .eq("auth_user_id", auth_user_id)
        .eq("status", "active")
        .limit(2)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated identity has no active AEOS user",
        )

    if len(response.data) != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated identity maps to an ambiguous AEOS user",
        )

    db_user = response.data[0]

    # An active membership in a suspended organization is not an active actor.
    # `organizations.status` is the tenant lifecycle control used for
    # offboarding, non-payment and breach containment; it must be enforced on
    # the application path as well as in RLS (see migration 004), because the
    # service-role client this function uses deliberately bypasses RLS.
    organization = (
        client.table("organizations")
        .select("id,status")
        .eq("id", db_user["organization_id"])
        .eq("status", "active")
        .limit(1)
        .execute()
    )

    if not organization.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated identity has no active AEOS organization",
        )

    return db_user


async def get_current_actor(db_user: dict = Depends(get_db_user)) -> AuthenticatedActor:
    """Build trusted tenant and role context exclusively from the database row."""
    try:
        return AuthenticatedActor(
            user_id=db_user["id"],
            organization_id=db_user["organization_id"],
            role=db_user["role"],
            auth_user_id=db_user["auth_user_id"],
        )
    except (KeyError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AEOS user record is invalid",
        ) from exc


PRIVILEGED_WRITE_ROLES = ("teacher", "admin")


def require_role(*allowed_roles: str):
    """Build a dependency that authorizes only actors whose server-derived role
    is one of ``allowed_roles``. The role itself always comes from the trusted
    database user row via ``get_current_actor`` — never from client input.
    """

    if not allowed_roles:
        raise ValueError("require_role must be given at least one allowed role")

    async def dependency(
        actor: AuthenticatedActor = Depends(get_current_actor),
    ) -> AuthenticatedActor:
        if actor.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This action requires teacher or admin authorization",
            )
        return actor

    return dependency


require_privileged_write = require_role(*PRIVILEGED_WRITE_ROLES)
