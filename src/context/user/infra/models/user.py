from datetime import datetime

from sqlalchemy import Index, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from context.user.public.enums.user import UserStatus
from infra.persistence.postgresql.columns import (
    created_at_column,
    timestamp_column,
    updated_at_column,
)
from infra.persistence.postgresql.models import BaseIntegerPK


class UserRow(BaseIntegerPK):
    __tablename__ = "users"
    __table_args__ = ({"schema": "user"},)

    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    status: Mapped[UserStatus] = mapped_column(
        ENUM(UserStatus, name="user_status_type", schema="user"),
        nullable=False,
    )
    status_until_at: Mapped[datetime | None] = timestamp_column(
        nullable=True,
        comment="User blocked until date.",
    )

    locale: Mapped[str] = mapped_column(String(64), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)

    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    inx_uu_status_until_at_blocked = Index(
        "inx_uu_status_until_at_blocked",
        status_until_at,
        postgresql_where=status == UserStatus.TEMPORARY_BLOCKED.value,
    )
