from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, and_
from sqlalchemy.orm import Mapped, mapped_column

from infra.persistence.postgresql.columns import (
    created_at_column,
    timestamp_column,
    updated_at_column,
)
from infra.persistence.postgresql.models import BaseIntegerPK


class UserEmailRow(BaseIntegerPK):
    __tablename__ = "user_emails"
    __table_args__ = ({"schema": "user"},)

    user_id: Mapped[int] = mapped_column(
        Integer(),
        ForeignKey("user.users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
    )
    verified_at: Mapped[datetime | None] = timestamp_column(nullable=True)
    revoked_at: Mapped[datetime | None] = timestamp_column(nullable=True)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    inx_uue_email_not_revoked_unq = Index(
        "inx_uue_email_not_revoked_unq",
        email,
        postgresql_where=revoked_at.is_(None),
        unique=True,
    )
    inx_uue_user_id_is_primary_unq = Index(
        "inx_uue_user_id_is_primary_unq",
        user_id,
        postgresql_where=and_(
            is_primary.is_(True),
            revoked_at.is_(None),
        ),
        unique=True,
    )
    inx_uue_user_id = Index(
        "inx_uue_user_id",
        user_id,
    )
