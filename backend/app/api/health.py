from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

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

    healthy = database_status == "connected"
    response = {
        "status": "ok" if healthy else "unavailable",
        "database": database_status,
    }
    if detail:
        response["detail"] = detail

    # Uptime checks and load balancers read the status code, not the body, so
    # an unusable database must not be reported as a healthy 200.
    return JSONResponse(
        response,
        status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
    )
