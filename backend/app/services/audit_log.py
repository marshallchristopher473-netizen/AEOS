"""Application-layer audit trail for sensitive records.

Writes that happen inside the database are audited there, in the same
transaction: AI feedback drafts and decisions (migration 006 triggers). This
module covers what no trigger can see, reads in particular.

Rows are written with the service-role client, so `organization_id` and
`performed_by` come only from the server-derived actor, never from the request.
A failed audit write fails the request, so a student record is not returned
without a trace of who read it.
"""

import logging

from fastapi import HTTPException, status

from app.models.schemas import AuthenticatedActor
from app.services.tenant_scope import insert_tenant_scoped_row

logger = logging.getLogger(__name__)


def record_audit_event(
    client,
    actor: AuthenticatedActor,
    *,
    entity_type: str,
    entity_id: str,
    action: str,
) -> None:
    try:
        insert_tenant_scoped_row(
            client,
            "audit_logs",
            {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "action": action,
                "performed_by": actor.user_id,
            },
            actor.organization_id,
        )
    except Exception as exc:
        # Log the error class only: database errors can echo the failing row.
        logger.error("audit write failed: action=%s error=%s", action, type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Audit log could not be written",
        ) from exc
