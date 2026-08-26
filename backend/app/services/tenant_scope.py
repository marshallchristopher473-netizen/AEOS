"""Tenant-scoping helpers for business routes.

These routes still use the Supabase service-role client (see
`app.services.supabase_service.get_supabase_admin_client`), which bypasses
Postgres RLS entirely. As of the last live check this session, RLS is
enabled on every table in the live project but has zero policies, so RLS
provides no functional access control today regardless of which client is
used - application-level scoping via these helpers is the only enforced
tenant boundary right now. Moving routes to a non-privileged,
RLS-respecting client and adding real RLS policies is separate, still
-required P0 work (RLS migrations are out of scope for this change); until
that lands, direct-database-access tests against RLS remain necessary and
are not satisfied by anything in this module.

Every helper here requires an explicit `organization_id` argument and never
trusts a caller-supplied one - the route layer is responsible for deriving
it from the authenticated actor before calling these.
"""
from typing import Any, Dict

from fastapi import HTTPException, status


def get_tenant_scoped_row(
    client, table: str, row_id: str, organization_id: str, not_found_detail: str
) -> Dict[str, Any]:
    """Fetch exactly one row by id, scoped to organization_id.

    Returns 404 whether the id does not exist at all or exists in a
    different tenant - the same response either way, so this endpoint
    cannot be used to discover whether an id belongs to another
    organization.
    """
    response = (
        client.table(table)
        .select("*")
        .eq("id", row_id)
        .eq("organization_id", organization_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail)
    return response.data[0]


def assert_related_row_in_tenant(
    client, table: str, row_id: str, organization_id: str, not_found_detail: str
) -> Dict[str, Any]:
    """Verify a referenced row (e.g. the student_id on an incoming
    assessment) belongs to organization_id before it is used to create a
    child row. Same not-found-regardless-of-reason behavior as
    get_tenant_scoped_row - do not use this to distinguish "doesn't exist"
    from "belongs to someone else" in the response.
    """
    return get_tenant_scoped_row(client, table, row_id, organization_id, not_found_detail)


def insert_tenant_scoped_row(client, table: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a row whose payload already carries a server-derived
    organization_id (and, where applicable, created_by). This function does
    not set those fields itself - the caller must have already derived them
    from the authenticated actor, never from client-supplied request data.
    """
    response = client.table(table).insert(payload).execute()
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{table} row could not be created",
        )
    return response.data[0]
