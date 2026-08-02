import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

load_dotenv()

security_scheme = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_JWKS_URL = f"{SUPABASE_URL.rstrip('/')}/auth/v1/jwks" if SUPABASE_URL else ""

_jwks: Optional[Dict[str, Any]] = None


async def get_jwks() -> Dict[str, Any]:
    global _jwks
    if _jwks is None:
        if not SUPABASE_JWKS_URL:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase URL is not configured",
            )

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(SUPABASE_JWKS_URL)
            resp.raise_for_status()
            _jwks = resp.json()
    return _jwks


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
):
    """Verify a JWT against Supabase's JWKS and return the decoded payload."""
    token = credentials.credentials

    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT is missing a key ID",
            )

        matching_key = next(
            (key for key in jwks.get("keys", []) if key.get("kid") == kid),
            None,
        )
        if matching_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWK not found",
            )

        payload = jwt.decode(
            token,
            matching_key,
            algorithms=["RS256"],
            options={"verify_exp": True, "verify_aud": False},
        )
        return payload
    except (JWTError, ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc
