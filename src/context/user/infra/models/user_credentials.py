from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from infra.persistence.postgresql.columns import (
    created_at_column,
    timestamp_column,
    updated_at_column,
)
from infra.persistence.postgresql.models import Base


class UserCredentialsRow(Base):
    __tablename__ = "user_credentials"
    __table_args__ = ({"schema": "user"},)

    user_id: Mapped[int] = mapped_column(
        Integer(),
        ForeignKey("user.users.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(60),
        nullable=True,
    )
    password_changed_at: Mapped[datetime] = timestamp_column(nullable=True)

    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()
