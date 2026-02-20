import uuid

from sqlalchemy import UUID, BigInteger, Integer, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True


class BaseIntegerPK(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)


class BaseBigIntegerPK(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)


class BaseUUIDPK(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        server_default=text("gen_random_uuid()"),
        primary_key=True,
    )
