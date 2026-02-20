from sqlalchemy import SmallInteger, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from context.money.public.enums.currency import CurrencyCode, CurrencyKind
from infra.persistence.postgresql.models import Base


class CurrencyRow(Base):
    __tablename__ = "currencies"
    __table_args__ = ({"schema": "money"},)

    code: Mapped[CurrencyCode] = mapped_column(
        String(16),
        nullable=False,
    )
    kind: Mapped[CurrencyKind] = mapped_column(
        ENUM(CurrencyKind, name="currency_kind_type", schema="money"),
        nullable=False,
    )
    precision: Mapped[int] = mapped_column(
        SmallInteger(),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
