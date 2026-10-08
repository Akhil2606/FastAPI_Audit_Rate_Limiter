from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import (
    AuditLogListResponse,
    AuditLogResponse,
)
from app.core.audit_cleanup import cleanup_old_audit_logs

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return current_user


@router.get(
    "",
    response_model=AuditLogListResponse,
)
def get_audit_logs(
    user_id: int | None = Query(default=None),
    endpoint: str | None = Query(default=None),
    status_code: int | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(AuditLog)

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)

    if endpoint is not None:
        query = query.filter(AuditLog.endpoint == endpoint)

    if status_code is not None:
        query = query.filter(
            AuditLog.status_code == status_code
        )

    if start_date is not None:
        query = query.filter(
            AuditLog.timestamp >= start_date
        )

    if end_date is not None:
        query = query.filter(
            AuditLog.timestamp <= end_date
        )

    total = query.count()

    total_pages = (
        (total + page_size - 1) // page_size
        if total > 0
        else 0
    )

    offset = (page - 1) * page_size

    items = (
        query
        .order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get(
    "/{log_id}",
    response_model=AuditLogResponse,
)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    audit_log = db.get(AuditLog, log_id)

    if not audit_log:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found",
        )

    return audit_log


@router.delete("/cleanup")
def cleanup_audit_logs(
    _: User = Depends(require_admin),
):
    deleted_count = cleanup_old_audit_logs()

    return {
        "message": "Old audit logs deleted successfully",
        "deleted_count": deleted_count,
    }