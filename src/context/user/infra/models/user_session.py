from datetime import date

from sqlalchemy import Boolean, ForeignKey, Index, Integer, false
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from infra.persistence.postgresql.columns import created_at_column
from infra.persistence.postgresql.models import BaseUUIDPK


class UserSessionRow(BaseUUIDPK):
    __tablename__ = "user_sessions"
    __table_args__ = ({"schema": "user"},)

    user_id: Mapped[int] = mapped_column(
        Integer(),
        ForeignKey("user.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_ip: Mapped[str] = mapped_column(
        INET(),
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        server_default=false(),
        comment="The flag changes its state when the 'AUTHORIZATION' type session is explicitly deleted. "
        "The expiration of the session lifetime is not reflected in the table, "
        "redis ttl is responsible for this.",
    )
    created_at: Mapped[date] = created_at_column()

    inx_uus_user_id_is_deleted_false = Index(
        "inx_uus_user_id_is_deleted_false",
        user_id,
        postgresql_where=is_deleted.is_(False),
    )
    inx_uus_user_id_created_at_desc = Index(
        "inx_uus_user_id_created_at_desc",
        user_id,
        created_at.desc(),
    )
