import pytest
from fastapi import HTTPException
from jose import JWTError

from fastapi.security import HTTPAuthorizationCredentials

from app.core import auth


@pytest.mark.asyncio
async def test_get_current_user_returns_payload_for_valid_token(monkeypatch):
    fake_jwk = {"kid": "test-kid", "kty": "RSA", "n": "abc", "e": "AQAB"}

    async def fake_get_jwks():
        return {"keys": [fake_jwk]}

    def fake_decode(token, key, algorithms, audience, issuer, options):
        assert token == "token"
        assert key == fake_jwk
        assert algorithms == ["RS256"]
        assert audience == "authenticated"
        assert issuer == auth.SUPABASE_ISSUER
        assert options == {"verify_exp": True, "verify_aud": True, "verify_iss": True}
        return {"sub": "user-123", "role": "authenticated"}

    monkeypatch.setattr(auth, "get_jwks", fake_get_jwks)
    monkeypatch.setattr(auth.jwt, "get_unverified_header", lambda token: {"kid": "test-kid"})
    monkeypatch.setattr(auth.jwt, "decode", fake_decode)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
    payload = await auth.get_current_user(credentials)

    assert payload["sub"] == "user-123"
    assert payload["role"] == "authenticated"


@pytest.mark.asyncio
async def test_get_current_user_raises_401_for_mismatched_audience(monkeypatch):
    fake_jwk = {"kid": "test-kid", "kty": "RSA", "n": "abc", "e": "AQAB"}

    async def fake_get_jwks():
        return {"keys": [fake_jwk]}

    def fake_decode(token, key, algorithms, audience, issuer, options):
        # Mirrors python-jose's real behavior: an audience mismatch raises a
        # JWTError subclass (JWTClaimsError) during verification.
        raise JWTError("Invalid audience")

    monkeypatch.setattr(auth, "get_jwks", fake_get_jwks)
    monkeypatch.setattr(auth.jwt, "get_unverified_header", lambda token: {"kid": "test-kid"})
    monkeypatch.setattr(auth.jwt, "decode", fake_decode)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_raises_401_for_mismatched_issuer(monkeypatch):
    fake_jwk = {"kid": "test-kid", "kty": "RSA", "n": "abc", "e": "AQAB"}

    async def fake_get_jwks():
        return {"keys": [fake_jwk]}

    def fake_decode(token, key, algorithms, audience, issuer, options):
        # Mirrors python-jose's real behavior: an issuer mismatch raises a
        # JWTError subclass (JWTClaimsError) during verification.
        raise JWTError("Invalid issuer")

    monkeypatch.setattr(auth, "get_jwks", fake_get_jwks)
    monkeypatch.setattr(auth.jwt, "get_unverified_header", lambda token: {"kid": "test-kid"})
    monkeypatch.setattr(auth.jwt, "decode", fake_decode)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_raises_401_for_missing_credentials():
    # HTTPBearer(auto_error=False) lets a missing Authorization header
    # reach get_current_user as credentials=None instead of the library's
    # default 403, so this and an invalid token both map to 401.
    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials=None)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_raises_401_for_missing_jwk(monkeypatch):
    async def fake_get_jwks():
        return {"keys": [{"kid": "other-kid"}]}

    monkeypatch.setattr(auth, "get_jwks", fake_get_jwks)
    monkeypatch.setattr(auth.jwt, "get_unverified_header", lambda token: {"kid": "test-kid"})

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401
