from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_user
from app.models.schemas import AuthenticatedActor
from app.services.supabase_service import get_supabase_admin_client


async def get_db_user(user_payload: dict = Depends(get_current_user)):
    """Return the internal AEOS user row for the authenticated Supabase user."""
    email = user_payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not in token",
        )

    client = get_supabase_admin_client()
    response = client.table("users").select("*").eq("email", email).limit(1).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in application",
        )

    return response.data[0]


async def get_current_actor(
    user_payload: dict = Depends(get_current_user),
) -> AuthenticatedActor:
    """Resolve the authenticated Supabase JWT to a trusted AEOS actor.

    `user_id`, `organization_id`, and `role` are read from the AEOS `users`
    row matched by `auth_user_id == JWT sub` — they are never taken from
    request bodies, query parameters, or the JWT payload itself (other than
    `sub`, which identifies which row to trust).
    """
    auth_user_id = user_payload.get("sub")
    if not auth_user_id or not isinstance(auth_user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT is missing a usable subject",
        )

    client = get_supabase_admin_client()
    response = (
        client.table("users")
        .select("*")
        .eq("auth_user_id", auth_user_id)
        .limit(2)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated identity has no AEOS user",
        )

    if len(response.data) > 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated identity maps to more than one AEOS user",
        )

    user_row = response.data[0]

    if user_row.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AEOS user is not active",
        )

    return AuthenticatedActor(
        user_id=user_row["id"],
        organization_id=user_row["organization_id"],
        role=user_row["role"],
        auth_user_id=auth_user_id,
    )
