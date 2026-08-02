# backend/app/core/dependencies.py
from fastapi import Depends, HTTPException, status
from .auth import get_current_user
from app.services.supabase_service import supabase_client  # adjust import to your actual client

async def get_db_user(user_payload: dict = Depends(get_current_user)):
    """Return the internal 'users' row for the authenticated Supabase user."""
    email = user_payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not in token")

    res = supabase_client.table("users").select("*").eq("email", email).execute()
    if not res.data or len(res.data) == 0:
        raise HTTPException(status_code=404, detail="User not found in application")

    return res.data[0]