from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_user
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
