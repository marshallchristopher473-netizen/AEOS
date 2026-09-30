from typing import Any, Dict, Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JOSEError

from app.core.config import (
    SUPABASE_JWKS_URL,
    SUPABASE_JWT_AUDIENCE,
    SUPABASE_JWT_ISSUER,
)

security_scheme = HTTPBearer(auto_error=False)

_jwks: Optional[Dict[str, Any]] = None


def unauthorized(detail: str = "Invalid authentication credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_jwks(force_refresh: bool = False) -> Dict[str, Any]:
    global _jwks
    if _jwks is None or force_refresh:
        if not SUPABASE_JWKS_URL:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWT verification is not configured",
            )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(SUPABASE_JWKS_URL)
                response.raise_for_status()
                candidate = response.json()
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication key service is unavailable",
            ) from exc

        if not isinstance(candidate, dict) or not isinstance(candidate.get("keys"), list):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication key service returned an invalid response",
            )
        _jwks = candidate
    return _jwks


def find_jwk(jwks: Dict[str, Any], kid: str) -> Optional[Dict[str, Any]]:
    return next(
        (key for key in jwks.get("keys", []) if key.get("kid") == kid),
        None,
    )


def signing_algorithm(jwk: Dict[str, Any]) -> Optional[str]:
    """Return the one algorithm a published key may verify, or None.

    Supabase signs sessions with an asymmetric key: ECC P-256 (ES256, its
    recommended default) or RSA (RS256). The algorithm is pinned by the key the
    token's `kid` selects, never taken from the token's own `alg` header, and
    each key type maps to exactly one algorithm. Symmetric ("oct") keys are
    never accepted: a shared secret that appears in a JWKS lets anyone mint
    tokens. The curve is checked here because python-jose will verify ES256
    over a P-384 key.

    A key that passes this check can still be unusable, for example an EC key
    published without its coordinates. python-jose then raises JWKError, which
    get_current_user turns into a 401 by catching JOSEError.
    """
    key_type = jwk.get("kty")
    if key_type == "RSA":
        algorithm = "RS256"
    elif key_type == "EC" and jwk.get("crv") == "P-256":
        algorithm = "ES256"
    else:
        return None

    declared = jwk.get("alg")
    if declared is not None and declared != algorithm:
        return None
    return algorithm


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
):
    """Verify a Supabase JWT and return only cryptographically trusted claims."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized("Not authenticated")

    if not SUPABASE_JWT_ISSUER or not SUPABASE_JWT_AUDIENCE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT issuer and audience must be configured",
        )

    token = credentials.credentials

    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not isinstance(kid, str) or not kid:
            raise unauthorized("JWT is missing a key ID")

        matching_key = find_jwk(await get_jwks(), kid)
        if matching_key is None:
            matching_key = find_jwk(await get_jwks(force_refresh=True), kid)
        if matching_key is None:
            raise unauthorized("JWT signing key is unknown")

        algorithm = signing_algorithm(matching_key)
        if algorithm is None:
            raise unauthorized("JWT signing key type is not supported")

        payload = jwt.decode(
            token,
            matching_key,
            algorithms=[algorithm],
            audience=SUPABASE_JWT_AUDIENCE,
            issuer=SUPABASE_JWT_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            },
        )
        # python-jose 3.3.0 returns early from `_validate_aud` when the `aud`
        # claim is absent, so `verify_aud: True` above rejects a WRONG audience
        # but silently accepts a MISSING one. Configuring an audience expresses
        # the intent that audience be enforced, so require the claim here.
        # This only ever rejects: no audience is inserted, inferred or defaulted.
        audience = payload.get("aud")
        if audience is None:
            raise unauthorized("JWT is missing the audience claim")
        presented = audience if isinstance(audience, (list, tuple)) else [audience]
        if SUPABASE_JWT_AUDIENCE not in presented:
            raise unauthorized("JWT audience is not accepted")

        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise unauthorized("JWT is missing a usable subject")
        return payload
    # JOSEError, not JWTError: python-jose raises JWKError (a JOSEError that is
    # not a JWTError) when the key selected by the caller's `kid` is not an RSA
    # key. Catching only JWTError let that escape as a 500 (SEC-G1-06).
    except (JOSEError, ValueError, TypeError) as exc:
        raise unauthorized() from exc
