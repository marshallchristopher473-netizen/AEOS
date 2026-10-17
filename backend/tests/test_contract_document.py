"""Keeps docs/BACKEND_IDENTITY_CONTRACT.md true to the running API.

The contract's endpoint table is what clients (the Next.js app, the Base44
prototype) are told they may call and with what authority. If a route, or the
access level its dependencies actually enforce, changes without the document
changing, these tests fail.
"""

from pathlib import Path

from fastapi.routing import APIRoute

from app.core.auth import get_current_user
from app.core.dependencies import get_current_actor, require_privileged_write
from app.main import app


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = BACKEND_DIR.parent
CONTRACT = REPOSITORY_ROOT / "docs" / "BACKEND_IDENTITY_CONTRACT.md"
ROUTES_START = "<!-- contract-routes:start -->"
ROUTES_END = "<!-- contract-routes:end -->"


def _dependency_calls(dependant):
    for dependency in dependant.dependencies:
        yield dependency.call
        yield from _dependency_calls(dependency)


def _enforced_access_level(route: APIRoute) -> str:
    calls = set(_dependency_calls(route.dependant))
    if require_privileged_write in calls:
        return "teacher_or_admin"
    if get_current_actor in calls:
        return "member"
    if get_current_user in calls:
        # A verified token with no resolved AEOS actor is not a documented
        # access level; surfacing it makes the comparison below fail loudly.
        return "token_without_actor"
    return "public"


def _implemented_routes():
    routes = {}
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods - {"HEAD"}:
            routes[(method, route.path)] = _enforced_access_level(route)
    return routes


def _documented_routes():
    contract = CONTRACT.read_text()
    assert ROUTES_START in contract and ROUTES_END in contract
    block = contract.split(ROUTES_START, 1)[1].split(ROUTES_END, 1)[0]

    routes = {}
    for line in block.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[0] in ("Method", "---"):
            continue
        method, path, access = cells
        assert (method, path) not in routes, f"duplicate contract row: {method} {path}"
        routes[(method, path)] = access
    return routes


def test_contract_documents_every_route_with_its_enforced_access_level():
    assert _documented_routes() == _implemented_routes()


def test_contract_token_requirements_match_the_verifier():
    contract = CONTRACT.read_text()
    verifier = (BACKEND_DIR / "app" / "core" / "auth.py").read_text()
    config = (BACKEND_DIR / "app" / "core" / "config.py").read_text()

    assert 'algorithms=["RS256"]' in verifier
    assert "**RS256 only**" in contract

    assert 'get_env("SUPABASE_JWT_AUDIENCE", "authenticated")' in config
    assert "default `authenticated`" in contract
