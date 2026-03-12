import uuid

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from context.wallet.application.enums.wallet import EntryDirection
from infra.persistence.postgresql.columns import created_at_column
from infra.persistence.postgresql.models import BaseUUIDPK
from infra.persistence.postgresql.types import sa_enum


class EntryRow(BaseUUIDPK):
    __tablename__ = "entries"
    __table_args__ = ({"schema": "wallet"},)

    operation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey("wallet.operations.id", ondelete="CASCADE"),
        nullable=False,
    )

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey("wallet.wallets.id", ondelete="CASCADE"),
        nullable=False,
    )

    direction: Mapped[EntryDirection] = mapped_column(
        sa_enum(EntryDirection, name="entry_direction_type", schema="wallet"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(),
        nullable=False,
        comment="Positive amount. Sign is defined by direction.",
    )

    created_at: Mapped[datetime] = created_at_column()

    inx_we_operation_id = Index(
        "inx_we_operation_id",
        operation_id,
    )
    inx_we_wallet_id_created_at_desc = Index(
        "inx_we_wallet_id_created_at_desc",
        wallet_id,
        created_at.desc(),
    )
