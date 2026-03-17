from collections.abc import Sequence
from dataclasses import dataclass

import pytest

from sqlalchemy import select

from context.user.infra.models import UserEmailRow
from infra.persistence.postgresql.connection import DBContext
from utils.query import BaseQuery


@dataclass()
class UserEmailQuery(BaseQuery[UserEmailRow, int]):
    async def get_by_user_id(self, user_id: int) -> Sequence[UserEmailRow]:
        async with self.db.session():
            stmt = select(UserEmailRow).where(UserEmailRow.user_id == user_id)
            result = await self.db.execute(stmt)
            return result.scalars().all()


@pytest.fixture()
def user_email_query(db_context: DBContext) -> UserEmailQuery:
    return UserEmailQuery(db_context, UserEmailRow, UserEmailRow.id)
