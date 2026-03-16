from collections.abc import Sequence
from dataclasses import dataclass

import pytest

from sqlalchemy import select

from context.user.infra.models import UserActionTokenRow
from infra.persistence.postgresql.connection import DBContext


@dataclass()
class GetUserActionTokensFactory:
    db: DBContext

    async def __call__(self) -> Sequence[UserActionTokenRow]:
        async with self.db.session():
            stmt = select(UserActionTokenRow)
            result = await self.db.execute(stmt)
            return result.scalars().all()


@pytest.fixture()
def get_user_action_tokens_factory(db_context: DBContext) -> GetUserActionTokensFactory:
    return GetUserActionTokensFactory(db_context)
