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
AI_PROVIDER = get_env("AI_PROVIDER", "placeholder")
