import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core import auth


@pytest.mark.asyncio
async def test_get_current_user_returns_payload_for_valid_token(monkeypatch):
    fake_jwk = {"kid": "test-kid", "kty": "RSA", "n": "abc", "e": "AQAB"}

    async def fake_get_jwks():
        return {"keys": [fake_jwk]}

    def fake_decode(token, key, algorithms, options):
        assert token == "token"
        assert key == fake_jwk
        assert algorithms == ["RS256"]
        assert options == {"verify_exp": True, "verify_aud": False}
        return {"sub": "user-123", "role": "authenticated"}

    monkeypatch.setattr(auth, "get_jwks", fake_get_jwks)
    monkeypatch.setattr(auth.jwt, "get_unverified_header", lambda token: {"kid": "test-kid"})
    monkeypatch.setattr(auth.jwt, "decode", fake_decode)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
    payload = await auth.get_current_user(credentials)

    assert payload["sub"] == "user-123"
    assert payload["role"] == "authenticated"


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
