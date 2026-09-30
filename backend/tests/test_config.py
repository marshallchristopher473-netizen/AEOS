import os
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]


def config_value(name, **env):
    """Read one setting from a fresh interpreter, so no module state leaks."""
    child_env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("SUPABASE_", "APP_", "DATABASE_"))
    }
    child_env.update(env)
    result = subprocess.run(
        [sys.executable, "-c", f"from app.core import config; print(config.{name})"],
        cwd=BACKEND,
        env=child_env,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


@pytest.mark.skipif(
    (BACKEND / ".env").exists(),
    reason="backend/.env overrides the environment, so the derived default is not observable",
)
def test_default_jwks_url_is_supabases_documented_discovery_endpoint():
    """The key set must be fetched from the endpoint Supabase documents.

    https://supabase.com/docs/guides/auth/signing-keys gives
    `GET https://project-id.supabase.co/auth/v1/.well-known/jwks.json`, and the
    official Python client requests `.well-known/jwks.json` under the Auth URL.
    A wrong default makes every authenticated request fail with 503.
    """
    assert (
        config_value("SUPABASE_JWKS_URL", SUPABASE_URL="https://project-ref.supabase.co/")
        == "https://project-ref.supabase.co/auth/v1/.well-known/jwks.json"
    )
