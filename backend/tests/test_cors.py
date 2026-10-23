from app.core.config import CORS_ALLOWED_ORIGINS

ALLOWED_ORIGIN = CORS_ALLOWED_ORIGINS[0]
FOREIGN_ORIGIN = "https://evil.example"


def preflight(client, origin):
    return client.options(
        "/students",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )


def test_teacher_portal_origin_passes_preflight(public_client):
    response = preflight(public_client, ALLOWED_ORIGIN)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert "authorization" in response.headers["access-control-allow-headers"].lower()
    assert "access-control-allow-credentials" not in response.headers


def test_foreign_origin_is_refused_at_preflight(public_client):
    response = preflight(public_client, FOREIGN_ORIGIN)

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_foreign_origin_gets_no_cors_header_on_requests(public_client):
    response = public_client.get("/health", headers={"Origin": FOREIGN_ORIGIN})

    assert "access-control-allow-origin" not in response.headers


def test_cors_does_not_bypass_authentication(public_client):
    response = public_client.get("/students", headers={"Origin": ALLOWED_ORIGIN})

    assert response.status_code == 401
