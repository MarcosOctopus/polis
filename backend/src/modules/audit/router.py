"""Audit router — list audit logs with filters."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.modules.auth.dependencies import get_current_user, get_db
from src.modules.audit.schemas import AuditLogFilter, AuditLogResponse
from src.modules.audit.service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("", response_model=dict)
async def list_audit_logs(
    tenant_id: str | None = Query(None),
    user_id: str | None = Query(None),
    action: str | None = Query(None),
    entity: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List audit logs with optional filters."""
    # Non-admin users can only see their own tenant's logs
    if not current_user.is_admin:
        if tenant_id and tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view logs for your own tenant",
            )
        tenant_id = current_user.tenant_id

    filters = AuditLogFilter(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        entity=entity,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )

    logs, total = await AuditService.list_logs(db, filters)
    return {
        "items": [AuditLogResponse.model_validate(log) for log in logs],
        "total": total,
        "skip": skip,
        "limit": limit,
    }
