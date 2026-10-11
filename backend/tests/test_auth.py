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


# Sentinel for make_token: removes a claim entirely rather than setting it.
# A claim that is ABSENT is a different input from one that is merely wrong,
# and python-jose treats the two differently for `aud`.
OMIT = object()


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
    for name, value in list(claims.items()):
        if value is OMIT:
            del claims[name]
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
async def test_token_with_no_audience_claim_is_401(configured_auth):
    """A validly signed token with the right issuer but NO `aud` must be rejected.

    This is not implied by `{"aud": "wrong-audience"}` above. python-jose 3.3.0
    returns early from `_validate_aud` when the claim is absent:

        if "aud" not in claims:
            # if audience:
            #     raise JWTError('Audience claim expected, but not in claims')
            return

    So `verify_aud: True` rejects a wrong audience but accepts a missing one.
    The token here is otherwise entirely valid — correct signing key, correct
    issuer, unexpired, usable subject — so the ONLY thing that can reject it is
    an explicit audience-presence check in `get_current_user`. Restoring
    missing-audience acceptance makes this test fail.
    """
    token = make_token(configured_auth, aud=OMIT)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    # Precondition: the claim really is absent, so this tests the missing-claim
    # path and not an accidentally-wrong-audience path.
    assert "aud" not in jwt.get_unverified_claims(token)

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
async def test_token_with_required_audience_is_still_accepted(configured_auth):
    """Positive control for the audience check.

    Without this, the two rejection tests above could be satisfied by an
    implementation that rejects every token.
    """
    token = make_token(configured_auth)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    payload = await auth.get_current_user(credentials)

    assert payload["aud"] == AUDIENCE
    assert payload["sub"] == "auth-user-a"


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


def _ec_public_jwk(kid):
    from cryptography.hazmat.primitives.asymmetric import ec

    numbers = ec.generate_private_key(ec.SECP256R1()).public_key().public_numbers()
    return {
        "kid": kid,
        "kty": "EC",
        "crv": "P-256",
        "alg": "ES256",
        "x": b64url_uint(numbers.x),
        "y": b64url_uint(numbers.y),
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "published_key",
    [
        pytest.param(_ec_public_jwk("test-kid"), id="non-rsa-key-under-the-token-kid"),
        pytest.param(
            {"kid": "test-kid", "kty": "oct", "k": "c3ltbWV0cmljLXNlY3JldA"},
            id="symmetric-key-under-the-token-kid",
        ),
    ],
)
async def test_unusable_published_key_is_401_not_a_server_error(
    monkeypatch, configured_auth, published_key
):
    """SEC-G1-06: a key python-jose cannot use must fail closed as 401.

    The token's `kid` selects the published key, and the caller chooses the
    `kid`. When that key is not an RSA key (an EC or a symmetric key), python-jose
    raises `JWKError`, which is a `JOSEError` but not a `JWTError`. Catching only
    `JWTError` let it escape as an unhandled exception, so the request
    returned 500 instead of 401. It never granted access, but a caller could
    turn any non-RSA key in the JWKS into server errors on demand.
    """
    token = make_token(configured_auth)

    async def jwks_with_unusable_key(force_refresh=False):
        return {"keys": [published_key]}

    monkeypatch.setattr(auth, "get_jwks", jwks_with_unusable_key)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401
