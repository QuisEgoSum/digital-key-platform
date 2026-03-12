from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
    UserActionTokenStatusType,
)
from infra.persistence.postgresql.columns import (
    created_at_column,
    timestamp_column,
    updated_at_column,
)
from infra.persistence.postgresql.models import BaseBigIntegerPK
from infra.persistence.postgresql.types import sa_enum


class UserActionTokenRow(BaseBigIntegerPK):
    __tablename__ = "user_action_tokens"
    __table_args__ = ({"schema": "user"},)

    user_id: Mapped[int] = mapped_column(
        Integer(),
        ForeignKey("user.users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    kind: Mapped[UserActionTokenKind] = mapped_column(
        sa_enum(UserActionTokenKind, name="user_auth_token_kind_type", schema="user"),
        nullable=False,
    )
    status: Mapped[UserActionTokenStatusType] = mapped_column(
        sa_enum(
            UserActionTokenStatusType,
            name="user_action_token_status_type",
            schema="user",
        ),
        nullable=False,
        server_default=UserActionTokenStatusType.ACTIVE.value,
    )

    channel: Mapped[UserActionTokenChannelType] = mapped_column(
        sa_enum(
            UserActionTokenChannelType,
            name="user_action_token_channel_type",
            schema="user",
        ),
        nullable=False,
    )
    channel_id: Mapped[int] = mapped_column(Integer(), nullable=False)

    short_token_hash: Mapped[str] = mapped_column(String(), nullable=False)
    long_token_hash: Mapped[str] = mapped_column(String(), nullable=False)

    expires_at: Mapped[datetime] = timestamp_column(nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    inx_uuat_user_id_created_at_desc = Index(
        "inx_uuat_user_id_created_at_desc",
        user_id,
        created_at.desc(),
    )
    inx_uuat_user_id_kind_status_active_unq = Index(
        "inx_uuat_user_id_kind_status_active_unq",
        user_id,
        kind,
        postgresql_where=status == UserActionTokenStatusType.ACTIVE.value,
        unique=True,
    )
