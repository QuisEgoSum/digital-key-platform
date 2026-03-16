from collections.abc import Sequence
from dataclasses import dataclass

import pytest

from sqlalchemy import select

from context.user.infra.models import UserEmailRow
from infra.persistence.postgresql.connection import DBContext


@dataclass()
class GetUserEmailsByUserIdFactory:
    db: DBContext

    async def __call__(self, user_id: int) -> Sequence[UserEmailRow]:
        async with self.db.session():
            stmt = select(UserEmailRow).where(UserEmailRow.user_id == user_id)
            result = await self.db.execute(stmt)
            return result.scalars().all()


@pytest.fixture()
def get_user_emails_by_user_id_factory(
    db_context: DBContext,
) -> GetUserEmailsByUserIdFactory:
    return GetUserEmailsByUserIdFactory(db_context)
