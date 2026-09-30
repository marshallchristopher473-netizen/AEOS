import os
import shutil
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


def config_value(tmp_path, name, **env):
    """Read one setting from a fresh interpreter, so no module state leaks.

    config.py loads `backend/.env` with override=True, so it runs from a copy of
    the `app` package that has no .env beside it. Otherwise a developer's own
    .env would decide the result.
    """
    shutil.copytree(BACKEND / "app", tmp_path / "app")
    child_env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("SUPABASE_", "APP_", "DATABASE_"))
    }
    child_env.update(env)
    result = subprocess.run(
        [sys.executable, "-c", f"from app.core import config; print(config.{name})"],
        cwd=tmp_path,
        env=child_env,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_default_jwks_url_is_supabases_documented_discovery_endpoint(tmp_path):
    """The key set must be fetched from the endpoint Supabase documents.

    https://supabase.com/docs/guides/auth/signing-keys gives
    `GET https://project-id.supabase.co/auth/v1/.well-known/jwks.json`, and the
    official Python client requests `.well-known/jwks.json` under the Auth URL.
    A wrong default makes every authenticated request fail with 503.
    """
    assert (
        config_value(tmp_path, "SUPABASE_JWKS_URL", SUPABASE_URL="https://project-ref.supabase.co/")
        == "https://project-ref.supabase.co/auth/v1/.well-known/jwks.json"
    )
