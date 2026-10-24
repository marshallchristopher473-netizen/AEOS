"""Loopback-only stand-in for Supabase Auth, for browser runs of the sign-in flow.

Implements only what the frontend's @supabase/ssr client calls: password and
refresh-token grants, the user lookup, logout, and the JWKS. Access tokens are
ES256-signed with a key generated at start-up and published by `kid`, so the
Next.js proxy verifies them with getClaims() the way it would against a hosted
project. Synthetic users only. Started by the fixture servers in this package;
never deploy it.
"""
import secrets
import threading
import time
import uuid

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from jose import jwk, jwt
from jose.exceptions import JOSEError

PORT = 9999
BASE_URL = f"http://127.0.0.1:{PORT}"
ISSUER = f"{BASE_URL}/auth/v1"
PASSWORD = "synthetic-password"
TOKEN_TTL_SECONDS = 3600

# Synthetic logins mapped to the auth subjects seeded in tests/fakes.py.
USERS = {
    "teacher@synthetic.aeos.test": "auth-user-a",
    "support@synthetic.aeos.test": "auth-support-a",
    "other-tenant@synthetic.aeos.test": "auth-user-b",
}

_KEY_ID = f"synthetic-{uuid.uuid4().hex[:12]}"
_PRIVATE_PEM = ec.generate_private_key(ec.SECP256R1()).private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
).decode()
_PUBLIC_JWK = {
    **jwk.construct(_PRIVATE_PEM, algorithm="ES256").public_key().to_dict(),
    "kid": _KEY_ID,
    "alg": "ES256",
    "use": "sig",
}
_refresh_tokens: dict = {}


def _issue_session(email: str) -> dict:
    now = int(time.time())
    subject = USERS[email]
    claims = {
        "iss": ISSUER,
        "sub": subject,
        "aud": "authenticated",
        "role": "authenticated",
        "email": email,
        "iat": now,
        "exp": now + TOKEN_TTL_SECONDS,
        "session_id": str(uuid.uuid4()),
    }
    refresh_token = secrets.token_urlsafe(24)
    _refresh_tokens[refresh_token] = email
    return {
        "access_token": jwt.encode(claims, _PRIVATE_PEM, algorithm="ES256", headers={"kid": _KEY_ID}),
        "token_type": "bearer",
        "expires_in": TOKEN_TTL_SECONDS,
        "expires_at": claims["exp"],
        "refresh_token": refresh_token,
        "user": _user(email),
    }


def _user(email: str) -> dict:
    return {
        "id": USERS[email],
        "aud": "authenticated",
        "role": "authenticated",
        "email": email,
        "app_metadata": {"provider": "email"},
        "user_metadata": {},
        "created_at": "2026-01-01T00:00:00Z",
    }


def verify_access_token(token: str):
    """Claims of a token this fixture issued and that is still valid, else None."""
    try:
        return jwt.decode(token, _PUBLIC_JWK, algorithms=["ES256"], audience="authenticated", issuer=ISSUER)
    except JOSEError:
        return None


def _invalid_credentials() -> JSONResponse:
    # Same body for an unknown email and a wrong password, as hosted Auth does.
    return JSONResponse(
        {"code": 400, "error_code": "invalid_credentials", "msg": "Invalid login credentials"},
        status_code=400,
    )


app = FastAPI(title="Synthetic Supabase Auth fixture")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/auth/v1/token")
async def token(request: Request, grant_type: str):
    body = await request.json()
    if grant_type == "password":
        email = str(body.get("email", "")).lower()
        if email not in USERS or not secrets.compare_digest(str(body.get("password", "")), PASSWORD):
            return _invalid_credentials()
        return _issue_session(email)
    if grant_type == "refresh_token":
        email = _refresh_tokens.pop(str(body.get("refresh_token", "")), None)
        if email is None:
            return JSONResponse({"code": 400, "error_code": "refresh_token_not_found", "msg": "Invalid Refresh Token"}, status_code=400)
        return _issue_session(email)
    return JSONResponse({"code": 400, "error_code": "unsupported_grant_type", "msg": "Unsupported grant type"}, status_code=400)


@app.get("/auth/v1/user")
async def user(authorization: str = Header(default="")):
    claims = verify_access_token(authorization.removeprefix("Bearer ").strip())
    if claims is None:
        return JSONResponse({"code": 401, "error_code": "bad_jwt", "msg": "invalid JWT"}, status_code=401)
    return _user(claims["email"])


@app.post("/auth/v1/logout")
async def logout():
    return Response(status_code=204)


@app.get("/auth/v1/.well-known/jwks.json")
async def jwks():
    return {"keys": [_PUBLIC_JWK]}


def start_in_background() -> None:
    """Serve on 127.0.0.1:PORT from a daemon thread of the calling fixture."""
    import uvicorn

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
