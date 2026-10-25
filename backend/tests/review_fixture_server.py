"""Loopback-only browser fixture: synthetic sessions/storage, production routes.

Run explicitly with AEOS_SYNTHETIC_REVIEW=1. Never deploy this test server.
Sessions come from the fake Supabase Auth server (tests/fake_supabase_auth.py),
started here on 127.0.0.1:9999; this fixture accepts only its signed tokens.
Production JWKS verification and PostgREST persistence are outside its scope.
"""
import os

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

from app.core.auth import get_current_user
from app.main import app
from app.services.supabase_service import get_supabase_admin_client
from tests import fake_supabase_auth
from tests.fakes import FakeClient, seeded_tables

bearer = HTTPBearer(auto_error=False)
database = FakeClient(seeded_tables())


async def synthetic_session(credentials=Depends(bearer)):
    claims = None if credentials is None else fake_supabase_auth.verify_access_token(credentials.credentials)
    if claims is None:
        raise HTTPException(status_code=401, detail="Synthetic session required")
    return {"sub": claims["sub"]}


if __name__ == "__main__":
    if os.environ.get("AEOS_SYNTHETIC_REVIEW") != "1":
        raise SystemExit("This synthetic fixture requires AEOS_SYNTHETIC_REVIEW=1")
    import uvicorn

    fake_supabase_auth.start_in_background()
    app.dependency_overrides[get_current_user] = synthetic_session
    app.dependency_overrides[get_supabase_admin_client] = lambda: database
    uvicorn.run(app, host="127.0.0.1", port=8000)
