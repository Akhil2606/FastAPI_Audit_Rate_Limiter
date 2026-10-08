from datetime import datetime, timedelta

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.audit_log import AuditLog


def cleanup_old_audit_logs():
    db = SessionLocal()

    try:
        cutoff_date = datetime.utcnow() - timedelta(
            days=settings.LOG_RETENTION_DAYS
        )

        deleted_count = (
            db.query(AuditLog)
            .filter(AuditLog.timestamp < cutoff_date)
            .delete(synchronize_session=False)
        )

        db.commit()

        return deleted_count

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()