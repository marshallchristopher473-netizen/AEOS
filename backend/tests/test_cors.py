import pytest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.core.config import parse_cors_allowed_origins
from app.main import app

PORTAL = "https://portal.aeos.test"
ATTACKER = "https://evil.example"


def _cors_middleware():
    matches = [m for m in app.user_middleware if m.cls is CORSMiddleware]
    assert len(matches) == 1, "exactly one CORS middleware must be registered"
    return matches[0]


@pytest.fixture
def portal_client():
    """The real app, with only its CORS allow-list pointed at a test portal."""
    middleware = _cors_middleware()
    original = middleware.kwargs["allow_origins"]
    middleware.kwargs["allow_origins"] = [PORTAL]
    app.middleware_stack = None
    app.dependency_overrides.clear()
    try:
        with TestClient(app) as client:
            yield client
    finally:
        middleware.kwargs["allow_origins"] = original
        app.middleware_stack = None


def _preflight(client, origin, method="GET"):
    return client.options(
        "/students",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": "authorization",
        },
    )


def test_cors_never_allows_credentials_or_wildcards():
    kwargs = _cors_middleware().kwargs
    assert kwargs["allow_credentials"] is False
    assert "*" not in kwargs["allow_origins"]
    assert "*" not in kwargs["allow_methods"]
    assert "*" not in kwargs["allow_headers"]


def test_allowed_origin_preflight_succeeds(portal_client):
    response = _preflight(portal_client, PORTAL)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == PORTAL
    assert "access-control-allow-credentials" not in response.headers


def test_disallowed_origin_preflight_is_rejected(portal_client):
    response = _preflight(portal_client, ATTACKER)

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_unlisted_method_preflight_is_rejected(portal_client):
    response = _preflight(portal_client, PORTAL, method="DELETE")

    assert response.status_code == 400


def test_disallowed_origin_gets_no_cors_grant_on_requests(portal_client):
    response = portal_client.get("/students", headers={"Origin": ATTACKER})

    assert response.status_code == 401
    assert "access-control-allow-origin" not in response.headers


def test_allowed_origin_still_requires_authentication(portal_client):
    response = portal_client.get("/students", headers={"Origin": PORTAL})

    assert response.status_code == 401
    assert response.headers["access-control-allow-origin"] == PORTAL


def test_parse_empty_allows_no_origins():
    assert parse_cors_allowed_origins("") == []
    assert parse_cors_allowed_origins(" , ") == []


def test_parse_trims_and_keeps_exact_origins():
    assert parse_cors_allowed_origins(f" {PORTAL} , http://localhost:3000 ") == [
        PORTAL,
        "http://localhost:3000",
    ]


@pytest.mark.parametrize(
    "raw",
    [
        "*",
        "https://*.aeos.test",
        "portal.aeos.test",
        "ftp://portal.aeos.test",
        "https://portal.aeos.test/app",
        "https://",
    ],
)
def test_parse_rejects_non_origin_entries(raw):
    with pytest.raises(ValueError):
        parse_cors_allowed_origins(raw)
