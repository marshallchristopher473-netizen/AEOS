"""Shared application-layer tenant scoping for service-role database access.

The server-only Supabase service role bypasses PostgreSQL RLS. Every business
query using that client must therefore receive a server-derived organization
identifier and apply it explicitly. Direct client/database access is defended
separately by the versioned RLS migration.
"""

from typing import Any, Dict, List
from uuid import uuid4

from fastapi import HTTPException, status


def list_tenant_scoped_rows(client, table: str, organization_id: str) -> List[Dict[str, Any]]:
    response = (
        client.table(table)
        .select("*")
        .eq("organization_id", organization_id)
        .execute()
    )
    return list(response.data or [])


def get_tenant_scoped_row(
    client,
    table: str,
    row_id: str,
    organization_id: str,
    not_found_detail: str,
) -> Dict[str, Any]:
    response = (
        client.table(table)
        .select("*")
        .eq("id", row_id)
        .eq("organization_id", organization_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_detail,
        )
    return response.data[0]


def assert_related_row_in_tenant(
    client,
    table: str,
    row_id: str,
    organization_id: str,
    not_found_detail: str,
) -> Dict[str, Any]:
    return get_tenant_scoped_row(
        client,
        table,
        row_id,
        organization_id,
        not_found_detail,
    )


def insert_tenant_scoped_row(
    client,
    table: str,
    payload: Dict[str, Any],
    organization_id: str,
) -> Dict[str, Any]:
    if "organization_id" in payload:
        raise ValueError("organization_id must be supplied by trusted server context")

    response = (
        client.table(table)
        .insert({"id": str(uuid4()), **payload, "organization_id": organization_id})
        .execute()
    )
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{table} row could not be created",
        )
    return response.data[0]
