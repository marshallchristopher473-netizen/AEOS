import pytest

from app.api import health


class _Probe:
    """Stands in for the Supabase client's `organizations` probe query."""

    def __init__(self, error=None):
        self.error = error

    def table(self, _name):
        return self

    def select(self, *_args):
        return self

    def limit(self, _value):
        return self

    def execute(self):
        if self.error is not None:
            raise self.error
        return None


def test_reachable_database_is_healthy(public_client, monkeypatch):
    monkeypatch.setattr(health, "get_supabase_client", lambda: _Probe())

    response = public_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_unconfigured_database_is_503(public_client, monkeypatch):
    def unconfigured():
        raise RuntimeError("Supabase URL and anon key must be configured")

    monkeypatch.setattr(health, "get_supabase_client", unconfigured)

    response = public_client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "unavailable"}


@pytest.mark.parametrize(
    "error, database",
    [
        (ConnectionError("connection refused"), "unavailable"),
        (Exception('relation "public.organizations" does not exist'), "schema_missing"),
        (Exception("Invalid API key"), "auth_error"),
    ],
)
def test_failed_database_probe_is_503(public_client, monkeypatch, error, database):
    monkeypatch.setattr(health, "get_supabase_client", lambda: _Probe(error))

    response = public_client.get("/health")

    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    assert response.json()["database"] == database
