from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Index, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from context.money.public.enums.currency import CurrencyCode
from context.wallet.public.enums.wallet import OwnerType, WalletRole
from infra.persistence.postgresql.columns import created_at_column, updated_at_column
from infra.persistence.postgresql.models import BaseUUIDPK


class WalletRow(BaseUUIDPK):
    __tablename__ = "wallets"
    __table_args__ = ({"schema": "wallet"},)

    owner_id: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        comment="Entity id in owner wallet.",
    )
    owner_type: Mapped[OwnerType] = mapped_column(
        ENUM(OwnerType, name="owner_type", schema="wallet"),
        nullable=False,
    )
    wallet_role: Mapped[WalletRole] = mapped_column(
        ENUM(WalletRole, name="wallet_role_type", schema="wallet"),
        nullable=False,
    )
    currency: Mapped[CurrencyCode | str] = mapped_column(
        String(16),
        nullable=False,
    )

    balance: Mapped[Decimal] = mapped_column(
        DECIMAL(),
        nullable=False,
        server_default="0",
        comment="The account balance is maintained for non-system wallets.",
    )

    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    inx_w_owner_id_owner_type_wallet_type_currency_unq = Index(
        "inx_w_owner_id_owner_type_wallet_type_currency_unq",
        owner_id,
        owner_type,
        wallet_role,
        currency,
        unique=True,
    )
