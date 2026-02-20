import uuid

from datetime import datetime
from typing import Any

from sqlalchemy import Index, String
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from context.wallet.public.enums.wallet import OperationSource, OperationType
from infra.persistence.postgresql.columns import created_at_column
from infra.persistence.postgresql.models import BaseUUIDPK


class OperationRow(BaseUUIDPK):
    __tablename__ = "operations"
    __table_args__ = ({"schema": "wallet"},)

    operation_type: Mapped[OperationType] = mapped_column(
        ENUM(OperationType, name="operation_type", schema="wallet"),
        nullable=False,
    )
    source_type: Mapped[OperationSource] = mapped_column(
        ENUM(OperationSource, name="operation_source_type", schema="wallet"),
        nullable=False,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        nullable=False,
        comment="Entity id in source BC (deposit_id/order_id/withdrawal_id/etc).",
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="Unique key to dedupe retries.",
    )

    currency: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        comment="Currency code for the entire operation. All entries must be in this currency.",
    )

    meta: Mapped[dict[str, Any]] = mapped_column(
        JSONB(),
        nullable=True,
        comment="Any metadata (product_id, comment, etc).",
    )

    created_at: Mapped[datetime] = created_at_column()

    inx_wo_idempotency_key_unq = Index(
        "inx_wo_idempotency_key_unq",
        idempotency_key,
        unique=True,
        postgresql_where=idempotency_key.isnot(None),
    )
    inx_wo_source_type_source_id = Index(
        "inx_wo_source_type_source_id",
        source_type,
        source_id,
    )
    inx_wo_created_at_desc = Index(
        "inx_wo_created_at_desc",
        created_at,
        postgresql_using="btree",
    )
