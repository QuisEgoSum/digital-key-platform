from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, TypeVar

from sqlalchemy import select

from infra.persistence.postgresql.connection import DBContext

TRow = TypeVar("TRow")
TPK = TypeVar("TPK")


@dataclass()
class BaseQuery[TRow, TPK]:
    db: DBContext
    model: type[TRow]
    pk_column: Any

    async def get(self, pk: TPK) -> TRow:
        async with self.db.session():
            stmt = select(self.model).where(self.pk_column == pk)
            result = await self.db.execute(stmt)
            return result.scalar_one()

    async def get_or_none(self, pk: TPK) -> TRow | None:
        async with self.db.session():
            stmt = select(self.model).where(self.pk_column == pk)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()

    async def all(self) -> Sequence[TRow]:
        async with self.db.session():
            print("self.pk_column", self.pk_column)
            stmt = select(self.model).order_by(self.pk_column.asc())
            result = await self.db.execute(stmt)
            return result.scalars().all()
