"""Loopback-only stand-in for the Supabase Auth endpoints the teacher portal calls.

Used only by the synthetic browser review (started by review_fixture_server.py
when AEOS_SYNTHETIC_REVIEW=1). It issues HS256 access tokens signed with a fixed
synthetic secret. supabase-js validates HS256 sessions by calling
GET /auth/v1/user, which this server answers after checking the signature,
expiry, and sign-out state. Never deploy this server or reuse its secret.
"""
import base64
import hashlib
import hmac
import json
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"
PORT = 9999
PORTAL_ORIGIN = "http://127.0.0.1:3000"
SYNTHETIC_PASSWORD = "synthetic-password"
SYNTHETIC_USERS = {
    "teacher@synthetic.aeos.test": "auth-user-a",
    "support@synthetic.aeos.test": "auth-support-a",
    "other-tenant@synthetic.aeos.test": "auth-user-b",
}
TOKEN_LIFETIME_SECONDS = 3600

_SECRET = b"aeos-synthetic-browser-review-only"
_lock = threading.Lock()
_signed_out_sessions: set[str] = set()
_refresh_tokens: dict[str, tuple[str, str]] = {}


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(segment: str) -> bytes:
    return base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4))


def _sign(signing_input: str) -> str:
    return _b64url(hmac.new(_SECRET, signing_input.encode(), hashlib.sha256).digest())


def issue_access_token(email: str, session_id: str) -> tuple[str, int]:
    expires_at = int(time.time()) + TOKEN_LIFETIME_SECONDS
    header = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url(json.dumps({
        "sub": SYNTHETIC_USERS[email],
        "email": email,
        "aud": "authenticated",
        "role": "authenticated",
        "session_id": session_id,
        "iat": expires_at - TOKEN_LIFETIME_SECONDS,
        "exp": expires_at,
    }).encode())
    return f"{header}.{payload}.{_sign(f'{header}.{payload}')}", expires_at


def verify_access_token(token: str) -> dict | None:
    """Claims of a token this server issued and has not signed out, else None."""
    parts = token.split(".")
    if len(parts) != 3:
        return None
    header, payload, signature = parts
    if not hmac.compare_digest(signature, _sign(f"{header}.{payload}")):
        return None
    try:
        claims = json.loads(_b64url_decode(payload))
    except ValueError:
        return None
    with _lock:
        signed_out = claims.get("session_id") in _signed_out_sessions
    if signed_out or not isinstance(claims.get("exp"), int) or claims["exp"] <= time.time():
        return None
    if claims.get("sub") not in SYNTHETIC_USERS.values():
        return None
    return claims


def _session(email: str, session_id: str) -> dict:
    access_token, expires_at = issue_access_token(email, session_id)
    refresh_token = secrets.token_urlsafe(24)
    with _lock:
        _refresh_tokens[refresh_token] = (email, session_id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": TOKEN_LIFETIME_SECONDS,
        "expires_at": expires_at,
        "refresh_token": refresh_token,
        "user": _user(email),
    }


def _user(email: str) -> dict:
    return {
        "id": SYNTHETIC_USERS[email],
        "aud": "authenticated",
        "role": "authenticated",
        "email": email,
        "app_metadata": {"provider": "email", "providers": ["email"]},
        "user_metadata": {},
        "created_at": "2026-01-01T00:00:00Z",
    }


class FakeSupabaseAuth(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stderr.write("fake-auth: " + format % args + "\n")

    def _send(self, status: int, body: dict | None = None):
        data = b"" if body is None else json.dumps(body).encode()
        self.send_response(status)
        origin = self.headers.get("Origin")
        if origin == PORTAL_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", PORTAL_ORIGIN)
            self.send_header("Vary", "Origin")
        if body is not None:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _error(self, status: int, code: str, message: str):
        self._send(status, {"code": status, "error_code": code, "msg": message})

    def _bearer_claims(self) -> dict | None:
        authorization = self.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return None
        return verify_access_token(authorization.removeprefix("Bearer "))

    def _json_body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return {}
        return body if isinstance(body, dict) else {}

    def do_OPTIONS(self):
        if self.headers.get("Origin") != PORTAL_ORIGIN:
            self._send(403)
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", PORTAL_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            self.headers.get("Access-Control-Request-Headers", "authorization, content-type"),
        )
        self.send_header("Vary", "Origin")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        if urlparse(self.path).path != "/auth/v1/user":
            self._error(404, "not_found", "Not found")
            return
        claims = self._bearer_claims()
        if claims is None:
            self._error(401, "bad_jwt", "invalid JWT")
            return
        self._send(200, _user(claims["email"]))

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/auth/v1/logout":
            claims = self._bearer_claims()
            if claims is not None:
                with _lock:
                    _signed_out_sessions.add(claims["session_id"])
            self._send(204)
            return
        if url.path != "/auth/v1/token":
            self._error(404, "not_found", "Not found")
            return

        grant_type = parse_qs(url.query).get("grant_type", [""])[0]
        body = self._json_body()
        if grant_type == "password":
            email = str(body.get("email", "")).strip().lower()
            password = str(body.get("password", ""))
            if email not in SYNTHETIC_USERS or not hmac.compare_digest(password, SYNTHETIC_PASSWORD):
                self._error(400, "invalid_credentials", "Invalid login credentials")
                return
            self._send(200, _session(email, secrets.token_hex(16)))
            return
        if grant_type == "refresh_token":
            with _lock:
                found = _refresh_tokens.pop(str(body.get("refresh_token", "")), None)
                if found is not None and found[1] in _signed_out_sessions:
                    found = None
            if found is None:
                self._error(400, "refresh_token_not_found", "Invalid Refresh Token")
                return
            self._send(200, _session(*found))
            return
        self._error(400, "unsupported_grant_type", "Unsupported grant type")


def start_in_background() -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((HOST, PORT), FakeSupabaseAuth)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
