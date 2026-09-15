import base64
import time

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from app.core import auth


ISSUER = "https://example.supabase.co/auth/v1"
AUDIENCE = "authenticated"


def b64url_uint(value: int) -> str:
    size = (value.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(value.to_bytes(size, "big")).rstrip(b"=").decode()


@pytest.fixture
def signing_material():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private_key.public_key().public_numbers()
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    jwk = {
        "kid": "test-kid",
        "kty": "RSA",
        "alg": "RS256",
        "use": "sig",
        "n": b64url_uint(public_numbers.n),
        "e": b64url_uint(public_numbers.e),
    }
    return private_pem, jwk


@pytest.fixture
def configured_auth(monkeypatch, signing_material):
    private_pem, public_jwk = signing_material

    async def fake_get_jwks(force_refresh=False):
        return {"keys": [public_jwk]}

    monkeypatch.setattr(auth, "SUPABASE_JWT_ISSUER", ISSUER)
    monkeypatch.setattr(auth, "SUPABASE_JWT_AUDIENCE", AUDIENCE)
    monkeypatch.setattr(auth, "get_jwks", fake_get_jwks)
    return private_pem


def make_token(private_pem, headers=None, **overrides):
    now = int(time.time())
    claims = {
        "sub": "auth-user-a",
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + 300,
        "email": "untrusted@example.test",
        "organization_id": "spoofed-org",
        "role": "spoofed-admin",
    }
    claims.update(overrides)
    return jwt.encode(
        claims,
        private_pem,
        algorithm="RS256",
        headers={"kid": "test-kid"} if headers is None else headers,
    )


@pytest.mark.asyncio
async def test_valid_signed_token_with_required_claims_is_accepted(configured_auth):
    token = make_token(configured_auth)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    payload = await auth.get_current_user(credentials)

    assert payload["sub"] == "auth-user-a"


@pytest.mark.asyncio
async def test_missing_credentials_are_401():
    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "claim_overrides",
    [
        {"aud": "wrong-audience"},
        {"iss": "https://attacker.invalid/auth/v1"},
        {"exp": int(time.time()) - 60},
        {"sub": ""},
    ],
)
async def test_invalid_required_claims_are_401(configured_auth, claim_overrides):
    token = make_token(configured_auth, **claim_overrides)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_forged_signature_is_401(configured_auth):
    attacker_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    attacker_pem = attacker_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    token = make_token(attacker_pem)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_unknown_signing_key_is_401(monkeypatch, configured_auth):
    token = make_token(configured_auth)

    async def no_matching_keys(force_refresh=False):
        return {"keys": [{"kid": "different-key"}]}

    monkeypatch.setattr(auth, "get_jwks", no_matching_keys)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_token_without_a_key_id_is_401(configured_auth):
    """M18(missing key ID): a token carrying no `kid` must be rejected outright.

    The dangerous weakening is not "no kid -> no key found" but "no kid -> try
    the keys we have anyway". This token is signed by the *real* key published
    in the JWKS, so any implementation that falls back to scanning or to
    `keys[0]` when the header is missing a `kid` would accept it. Selecting a
    verification key must be driven by the header, never guessed.
    """
    token = make_token(configured_auth, headers={"alg": "RS256", "typ": "JWT"})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_unknown_key_id_is_401_even_though_a_usable_key_is_published(
    configured_auth,
):
    """M18(unknown key ID): an unmatched `kid` must be rejected, not worked around.

    `test_unknown_signing_key_is_401` publishes a JWKS with no usable key, so it
    would still pass against an implementation that ignores `kid` and tries every
    published key. Here the JWKS holds the *real* signing key under `test-kid`
    while the token claims `kid: rotated-out-kid`. Rejection therefore proves the
    unknown-kid branch itself is live, which is what makes key rotation and
    revocation mean anything.
    """
    token = make_token(
        configured_auth, headers={"alg": "RS256", "typ": "JWT", "kid": "rotated-out-kid"}
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_malformed_token_is_401(configured_auth):
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="not-a-jwt",
    )

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401
