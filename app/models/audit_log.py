from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    endpoint: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    method: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        index=True
    )

    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    response_time: Mapped[float] = mapped_column(
        nullable=False
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )