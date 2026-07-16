from functools import lru_cache

from supabase import create_client, Client

from app.core.config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise RuntimeError("Supabase URL and anon key must be configured")

    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


@lru_cache(maxsize=1)
def get_supabase_admin_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("Supabase service role key must be configured")

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
