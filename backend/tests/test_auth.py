import base64
import hashlib
import hmac
import json
import time

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWKError

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


def make_token(private_pem, headers=None, algorithm="RS256", **overrides):
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
        algorithm=algorithm,
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

    This is not implied by `{"aud": "wrong-audience"}` above. python-jose 3.3.0-3.5.0
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
async def test_token_with_no_expiry_claim_is_401(configured_auth):
    """A validly signed token with NO `exp` must be rejected: it would never expire.

    python-jose 3.3.0-3.5.0 treats `exp` as optional (`_validate_exp` returns early
    when the claim is absent), so `verify_exp: True` alone accepts this token.
    It is otherwise entirely valid, so the only thing that can reject it is the
    explicit expiry-presence check in `get_current_user`.
    """
    token = make_token(configured_auth, exp=OMIT)
    public_jwk = (await auth.get_jwks())["keys"][0]

    # Preconditions: the claim really is absent, and python-jose alone accepts
    # the token, so the rejection below comes from our check.
    assert "exp" not in jwt.get_unverified_claims(token)
    assert jwt.decode(
        token, public_jwk, algorithms=["RS256"], audience=AUDIENCE, issuer=ISSUER
    )["sub"] == "auth-user-a"

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
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


# ---------------------------------------------------------------------------
# Signing algorithm pinned by the published key
#
# Supabase signs sessions with ES256 (ECC P-256, its recommended default) or
# RS256. A JWKS may hold both during a key rotation. Each published key allows
# exactly one algorithm, chosen from the key and never from the token header.
# ---------------------------------------------------------------------------


EC_KID = "test-ec-kid"


def b64url_bytes(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def b64url_coordinate(value: int, size: int) -> str:
    # RFC 7518 §6.2.1.2: EC coordinates are always the full size of the curve.
    return b64url_bytes(value.to_bytes(size, "big"))


def pkcs8_pem(private_key) -> bytes:
    return private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


def ec_public_jwk(private_key, kid=EC_KID, crv="P-256", size=32, alg="ES256"):
    numbers = private_key.public_key().public_numbers()
    jwk = {
        "kid": kid,
        "kty": "EC",
        "crv": crv,
        "use": "sig",
        "key_ops": ["verify"],
        "ext": True,
        "x": b64url_coordinate(numbers.x, size),
        "y": b64url_coordinate(numbers.y, size),
    }
    if alg is not None:
        jwk["alg"] = alg
    return jwk


def hand_built_token(header, claims, sign):
    """Build a JWT byte by byte, for tokens python-jose refuses to encode."""
    signing_input = ".".join(
        b64url_bytes(json.dumps(part, separators=(",", ":")).encode())
        for part in (header, claims)
    )
    return f"{signing_input}.{b64url_bytes(sign(signing_input.encode()))}"


def valid_claims():
    now = int(time.time())
    return {"sub": "auth-user-a", "iss": ISSUER, "aud": AUDIENCE, "iat": now, "exp": now + 300}


@pytest.fixture
def ec_private_key():
    return ec.generate_private_key(ec.SECP256R1())


@pytest.fixture
def both_key_types(monkeypatch, signing_material, ec_private_key):
    """A JWKS publishing an RSA key and an EC P-256 key, as during a rotation."""
    rsa_pem, rsa_jwk = signing_material

    async def fake_get_jwks(force_refresh=False):
        return {"keys": [rsa_jwk, ec_public_jwk(ec_private_key)]}

    monkeypatch.setattr(auth, "SUPABASE_JWT_ISSUER", ISSUER)
    monkeypatch.setattr(auth, "SUPABASE_JWT_AUDIENCE", AUDIENCE)
    monkeypatch.setattr(auth, "get_jwks", fake_get_jwks)
    return rsa_pem, pkcs8_pem(ec_private_key)


def publish_only(monkeypatch, *keys):
    async def fake_get_jwks(force_refresh=False):
        return {"keys": list(keys)}

    monkeypatch.setattr(auth, "get_jwks", fake_get_jwks)


async def assert_rejected(token):
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)
    assert exc_info.value.status_code == 401
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
@pytest.mark.parametrize("key_type", ["RS256", "ES256"])
async def test_token_signed_by_either_published_key_type_is_accepted(
    both_key_types, key_type
):
    """Positive control: both Supabase key types verify, side by side.

    Without this, every rejection test below could be satisfied by an
    implementation that rejects all ES256 tokens, which is what an RS256-only
    backend does to every login on a project using Supabase's default key.
    """
    rsa_pem, ec_pem = both_key_types
    if key_type == "RS256":
        token = make_token(rsa_pem)
    else:
        token = make_token(ec_pem, headers={"kid": EC_KID}, algorithm="ES256")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    payload = await auth.get_current_user(credentials)

    assert payload["sub"] == "auth-user-a"
    assert payload["aud"] == AUDIENCE


@pytest.mark.asyncio
async def test_es256_token_signed_by_an_unpublished_key_is_401(both_key_types):
    attacker_pem = pkcs8_pem(ec.generate_private_key(ec.SECP256R1()))
    await assert_rejected(
        make_token(attacker_pem, headers={"kid": EC_KID}, algorithm="ES256")
    )


@pytest.mark.asyncio
async def test_es256_token_still_enforces_the_required_claims(both_key_types):
    _, ec_pem = both_key_types
    await assert_rejected(
        make_token(
            ec_pem, headers={"kid": EC_KID}, algorithm="ES256", aud="wrong-audience"
        )
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case",
    [
        "rs512-signed-by-the-published-rsa-key",
        "es256-token-naming-the-rsa-key",
        "rs256-token-naming-the-ec-key",
        "hs256-keyed-with-the-rsa-public-key",
        "hs256-keyed-with-the-rsa-public-key-der",
        "unsigned-alg-none",
    ],
)
async def test_algorithm_the_published_key_does_not_allow_is_401(both_key_types, case):
    """M18j: the token header must not choose the verification algorithm.

    `rs512-signed-by-the-published-rsa-key` is signed by the REAL private key
    whose public half is published for RS256. Only pinning the algorithm to the
    key rejects it; an implementation that verifies with the header's `alg`
    accepts it. The HS256 case is the classic confusion attack: the attacker
    uses the published RSA public key as an HMAC secret.
    """
    rsa_pem, ec_pem = both_key_types
    claims = valid_claims()
    if case == "rs512-signed-by-the-published-rsa-key":
        token = make_token(rsa_pem, algorithm="RS512")
    elif case == "es256-token-naming-the-rsa-key":
        token = make_token(ec_pem, algorithm="ES256")
    elif case == "rs256-token-naming-the-ec-key":
        token = make_token(rsa_pem, headers={"kid": EC_KID})
    elif case.startswith("hs256-keyed-with-the-rsa-public-key"):
        # PEM is the CVE-2024-33663 shape; bare DER is GHSA-3qf3-8w2g-rqmx,
        # which python-jose through 3.5.0 still accepts as an HMAC secret when
        # the caller does not restrict the algorithm.
        encoding = (
            serialization.Encoding.DER if case.endswith("-der") else serialization.Encoding.PEM
        )
        public_bytes = (
            serialization.load_pem_private_key(rsa_pem, password=None)
            .public_key()
            .public_bytes(encoding, serialization.PublicFormat.SubjectPublicKeyInfo)
        )
        token = hand_built_token(
            {"alg": "HS256", "typ": "JWT", "kid": "test-kid"},
            claims,
            lambda data: hmac.new(public_bytes, data, hashlib.sha256).digest(),
        )
    else:
        token = hand_built_token(
            {"alg": "none", "typ": "JWT", "kid": "test-kid"}, claims, lambda data: b""
        )

    await assert_rejected(token)


@pytest.mark.asyncio
async def test_symmetric_key_in_the_jwks_is_never_accepted(monkeypatch, configured_auth):
    """M18i: a shared secret must never verify a token, even when published.

    Supabase's self-hosting guide builds a key set for its internal services
    that includes the legacy HS256 `JWT_SECRET` as an "oct" key. If a set like
    that ever reached this backend and it accepted the key, anyone who can read
    the set could mint a session for any user. The token below is correctly
    signed with that secret, so the only thing that can reject it is the
    refusal to use symmetric keys at all.
    """
    secret = b"legacy-jwt-secret-that-is-now-public-0123456789"
    oct_jwk = {"kid": "test-kid", "kty": "oct", "alg": "HS256", "k": b64url_bytes(secret)}
    publish_only(monkeypatch, oct_jwk)
    token = jwt.encode(valid_claims(), secret, algorithm="HS256", headers={"kid": "test-kid"})

    # Precondition: python-jose alone accepts this token, so the rejection
    # below comes from our key policy and not from a malformed fixture.
    assert jwt.decode(token, oct_jwk, algorithms=["HS256"], audience=AUDIENCE)["sub"]

    await assert_rejected(token)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case",
    [
        "ec-p384-key",
        "ec-p384-key-declared-es256",
        "rsa-key-declared-for-rs512",
        "rsa-key-declared-for-es256",
        "ec-p256-entry-wrapping-nested-keys",
    ],
)
async def test_published_key_this_backend_must_not_use_is_401_even_if_jose_accepts(
    monkeypatch, configured_auth, signing_material, case
):
    """Each token below is correctly signed and python-jose alone accepts it.

    Only RSA/RS256 and EC P-256/ES256 keys may verify, and only for the one
    algorithm the key is published for. The P-384 cases matter because
    python-jose verifies ES256 over a P-384 key. The declared-alg cases sign
    RS256 with the REAL published RSA key, so only the declared-alg check can
    reject them. The nested-keys case (M18k) is a P-256 entry wrapping a P-384
    key: python-jose treats any dict with a "keys" member as a key set, so
    handing it the raw entry would verify against the key it wraps.
    """
    _, rsa_jwk = signing_material
    if case.startswith("ec-p384-key"):
        p384 = ec.generate_private_key(ec.SECP384R1())
        declared = "ES256" if case.endswith("declared-es256") else None
        published = ec_public_jwk(p384, kid="test-kid", crv="P-384", size=48, alg=declared)
        token = make_token(pkcs8_pem(p384), algorithm="ES256")
    elif case.startswith("rsa-key-declared-for"):
        published = {**rsa_jwk, "alg": case.rsplit("-", 1)[1].upper()}
        token = make_token(configured_auth)
    else:
        p384 = ec.generate_private_key(ec.SECP384R1())
        wrapped = ec_public_jwk(p384, kid="test-kid", crv="P-384", size=48, alg=None)
        published = {
            **ec_public_jwk(ec.generate_private_key(ec.SECP256R1()), kid="test-kid"),
            "keys": [wrapped],
        }
        token = make_token(pkcs8_pem(p384), algorithm="ES256")

    # Precondition: python-jose alone accepts the token, so the rejection
    # below comes from our key policy and not from a broken fixture.
    algorithm = jwt.get_unverified_header(token)["alg"]
    assert jwt.decode(token, published, algorithms=[algorithm], audience=AUDIENCE)["sub"]

    publish_only(monkeypatch, published)
    await assert_rejected(token)


@pytest.mark.asyncio
async def test_published_okp_key_is_401(monkeypatch, configured_auth):
    """Ed25519 ("OKP") is not a key type this backend verifies with."""
    public_raw = (
        ed25519.Ed25519PrivateKey.generate()
        .public_key()
        .public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    )
    publish_only(
        monkeypatch,
        {"kid": "test-kid", "kty": "OKP", "crv": "Ed25519", "x": b64url_bytes(public_raw)},
    )
    await assert_rejected(make_token(configured_auth))


@pytest.mark.asyncio
async def test_published_key_python_jose_cannot_load_is_401_not_a_server_error(
    monkeypatch, configured_auth, ec_private_key
):
    """An EC P-256 key published without its coordinates must fail closed as 401.

    The key passes the type check, so it reaches python-jose, which raises
    `JWKError`. That is a JOSEError but not a JWTError, so a handler that
    catches only JWTError returns 500. This is the one remaining path to
    `JWKError` once each key type is pinned to its algorithm.
    """
    incomplete = ec_public_jwk(ec_private_key)
    del incomplete["x"], incomplete["y"]
    publish_only(monkeypatch, incomplete)
    token = make_token(pkcs8_pem(ec_private_key), headers={"kid": EC_KID}, algorithm="ES256")

    # Precondition: this really is the JWKError path.
    with pytest.raises(JWKError):
        jwt.decode(token, incomplete, algorithms=["ES256"], audience=AUDIENCE)

    await assert_rejected(token)


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
        pytest.param(_ec_public_jwk("test-kid"), id="ec-p256-key-under-the-rs256-tokens-kid"),
        pytest.param(
            {"kid": "test-kid", "kty": "oct", "k": "c3ltbWV0cmljLXNlY3JldA"},
            id="symmetric-key-under-the-token-kid",
        ),
    ],
)
async def test_unusable_published_key_is_401_not_a_server_error(
    monkeypatch, configured_auth, published_key
):
    """SEC-G1-06 regression: an RS256 token whose `kid` names a non-RSA key is 401.

    The token's `kid` selects the published key, and the caller chooses the
    `kid`. Against an RS256-only verifier, both keys below made python-jose
    raise `JWKError` (a `JOSEError` but not a `JWTError`), which escaped the
    401 handler as a 500. With each key type now pinned to one algorithm
    (`signing_algorithm`), neither case reaches `JWKError` any more: the EC
    P-256 key is used for ES256 and the RS256 signature fails to verify, and the
    symmetric key is refused before python-jose sees it. Both must still fail
    closed as 401. The remaining `JWKError` path, and the test that kills M18h,
    is `test_published_key_python_jose_cannot_load_is_401_not_a_server_error`.
    """
    token = make_token(configured_auth)

    async def jwks_with_unusable_key(force_refresh=False):
        return {"keys": [published_key]}

    monkeypatch.setattr(auth, "get_jwks", jwks_with_unusable_key)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(credentials)

    assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# Key-set cache: a key the issuer stops publishing must stop verifying.
#
# These run the real `get_jwks` against an in-process HTTP transport, so the
# cache, its expiry and its refresh are exercised rather than replaced.
# ---------------------------------------------------------------------------


JWKS_URL = "https://example.supabase.co/auth/v1/.well-known/jwks.json"


@pytest.fixture
def live_jwks(monkeypatch):
    """Serve a mutable key set to the real `get_jwks`, starting from an empty cache.

    Returns the state dict: assign `state["body"]` to change what is published,
    `state["status"]` to make the endpoint fail; `state["fetches"]` counts
    requests.
    """
    import httpx

    state = {"body": {"keys": []}, "status": 200, "fetches": 0}

    def serve(request):
        state["fetches"] += 1
        assert str(request.url) == JWKS_URL
        return httpx.Response(state["status"], json=state["body"])

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        auth.httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(serve), **kwargs),
    )
    monkeypatch.setattr(auth, "SUPABASE_JWKS_URL", JWKS_URL)
    monkeypatch.setattr(auth, "SUPABASE_JWT_ISSUER", ISSUER)
    monkeypatch.setattr(auth, "SUPABASE_JWT_AUDIENCE", AUDIENCE)
    monkeypatch.setattr(auth, "_jwks", None)
    monkeypatch.setattr(auth, "_jwks_fetched_at", 0.0)
    return state


def age_cached_key_set(monkeypatch):
    """Make the cached key set exactly one second older than its maximum age."""
    monkeypatch.setattr(
        auth, "_jwks_fetched_at", time.monotonic() - auth.JWKS_MAX_AGE_SECONDS - 1
    )


async def verify(token):
    return await auth.get_current_user(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    )


@pytest.mark.asyncio
async def test_revoked_signing_key_is_refused_once_the_cached_key_set_expires(
    monkeypatch, live_jwks, signing_material
):
    """A key removed from the JWKS must stop verifying within the cache's max age.

    Before the max age, a matching `kid` is served from cache and never causes a
    refresh, so without an expiry a revoked key verifies tokens for as long as
    the process lives. The token here is correctly signed by that key and is
    otherwise valid; only the refresh can reject it.
    """
    private_pem, public_jwk = signing_material
    live_jwks["body"] = {"keys": [public_jwk]}
    token = make_token(private_pem)

    # Positive control: while the key is published it verifies.
    assert (await verify(token))["sub"] == "auth-user-a"

    # The issuer revokes the key and publishes a replacement.
    replacement = {**public_jwk, "kid": "replacement-kid"}
    live_jwks["body"] = {"keys": [replacement]}
    age_cached_key_set(monkeypatch)

    await assert_rejected(token)
    # 1: initial fetch. 2: refresh because the cached set expired. 3: the
    # existing forced refresh, because the refreshed set no longer has the kid.
    assert live_jwks["fetches"] == 3


@pytest.mark.asyncio
async def test_cached_key_set_is_reused_within_its_max_age(live_jwks, signing_material):
    """The key set is not refetched for every request while it is fresh."""
    private_pem, public_jwk = signing_material
    live_jwks["body"] = {"keys": [public_jwk]}
    token = make_token(private_pem)

    await verify(token)
    await verify(token)

    assert live_jwks["fetches"] == 1


@pytest.mark.asyncio
async def test_expired_key_set_is_not_used_when_its_refresh_fails(
    monkeypatch, live_jwks, signing_material
):
    """When a due refresh fails, verification fails closed instead of trusting the
    expired set."""
    private_pem, public_jwk = signing_material
    live_jwks["body"] = {"keys": [public_jwk]}
    token = make_token(private_pem)
    assert (await verify(token))["sub"] == "auth-user-a"

    live_jwks["status"] = 500
    age_cached_key_set(monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        await verify(token)
    assert exc_info.value.status_code == 503
