"""Loopback-only browser fixture: synthetic sessions/storage, production routes.

Run explicitly with AEOS_SYNTHETIC_REVIEW=1. Never deploy this test server.
JWT verification and PostgREST persistence are outside this fixture's scope.
"""
import os

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

from app.core.auth import get_current_user
from app.main import app
from app.services.supabase_service import get_supabase_admin_client
from tests.fakes import FakeClient, seeded_tables

bearer = HTTPBearer(auto_error=False)
database = FakeClient(seeded_tables())


async def synthetic_session(credentials=Depends(bearer)):
    subjects = {
        "synthetic-teacher": "auth-user-a",
        "synthetic-support": "auth-support-a",
        "synthetic-other-tenant": "auth-user-b",
    }
    if credentials is None or credentials.credentials not in subjects:
        raise HTTPException(status_code=401, detail="Synthetic session required")
    return {"sub": subjects[credentials.credentials]}


if __name__ == "__main__":
    if os.environ.get("AEOS_SYNTHETIC_REVIEW") != "1":
        raise SystemExit("This synthetic fixture requires AEOS_SYNTHETIC_REVIEW=1")
    import uvicorn

    app.dependency_overrides[get_current_user] = synthetic_session
    app.dependency_overrides[get_supabase_admin_client] = lambda: database
    uvicorn.run(app, host="127.0.0.1", port=8000)
