from fastapi import APIRouter

from app.services.supabase_service import get_supabase_client

router = APIRouter(tags=["health"])


def _classify_database_error(exc: Exception) -> tuple[str, str | None]:
    message = str(exc).lower()

    if "relation" in message and "does not exist" in message:
        return (
            "schema_missing",
            "The required Supabase tables have not been created yet. Run the SQL in AEOS_Supabase_Setup.sql in the Supabase SQL editor.",
        )

    if "invalid api key" in message or "api key" in message:
        return (
            "auth_error",
            "The Supabase URL or API key is invalid. Verify the environment values in backend/.env.",
        )

    return "unavailable", None


@router.get("/health")
def health_check():
    try:
        client = get_supabase_client()
        client.table("organizations").select("id").limit(1).execute()
        database_status = "connected"
        detail = None
    except Exception as exc:
        database_status, detail = _classify_database_error(exc)

    response = {
        "status": "ok",
        "database": database_status,
    }
    if detail:
        response["detail"] = detail

    return response
