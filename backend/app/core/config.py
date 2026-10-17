import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE, override=True)


def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


APP_ENV = get_env("APP_ENV", "development")
DEBUG = get_env("DEBUG", "true").lower() == "true"
DATABASE_URL = get_env("DATABASE_URL")
SUPABASE_URL = get_env("SUPABASE_URL")
SUPABASE_ANON_KEY = get_env("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = get_env("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_JWKS_URL = get_env(
    "SUPABASE_JWKS_URL",
    f"{SUPABASE_URL.rstrip('/')}/auth/v1/jwks" if SUPABASE_URL else "",
)
SUPABASE_JWT_ISSUER = get_env(
    "SUPABASE_JWT_ISSUER",
    f"{SUPABASE_URL.rstrip('/')}/auth/v1" if SUPABASE_URL else "",
)
SUPABASE_JWT_AUDIENCE = get_env("SUPABASE_JWT_AUDIENCE", "authenticated")
AI_PROVIDER = get_env("AI_PROVIDER", "placeholder")


def parse_cors_allowed_origins(raw: str) -> list[str]:
    """Parse a comma-separated list of exact browser origins.

    Fails closed: an empty value allows no cross-origin browser access. A
    wildcard, a path, or a non-http(s) scheme is a configuration error rather
    than something to silently widen or repair, because every allowed origin
    can make authenticated calls with a teacher's bearer token.
    """
    origins: list[str] = []
    for entry in raw.split(","):
        origin = entry.strip()
        if not origin:
            continue
        if "*" in origin:
            raise ValueError("CORS_ALLOWED_ORIGINS must list exact origins, not wildcards")
        scheme, sep, host = origin.partition("://")
        if scheme not in ("http", "https") or not sep or not host or "/" in host:
            raise ValueError(f"CORS_ALLOWED_ORIGINS entry is not a bare origin: {origin!r}")
        origins.append(origin)
    return origins


CORS_ALLOWED_ORIGINS = parse_cors_allowed_origins(get_env("CORS_ALLOWED_ORIGINS"))
