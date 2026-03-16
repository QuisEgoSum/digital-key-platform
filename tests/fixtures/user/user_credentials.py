from dataclasses import dataclass

import pytest

from sqlalchemy import select

from context.user.infra.models import UserCredentialsRow
from infra.persistence.postgresql.connection import DBContext


@dataclass()
class GetUserCredentialsByUserIDFactory:
    db: DBContext

    async def __call__(self, user_id: int) -> UserCredentialsRow:
        async with self.db.session():
            stmt = select(UserCredentialsRow).where(
                UserCredentialsRow.user_id == user_id,
            )
            result = await self.db.execute(stmt)
            return result.scalar_one()


@pytest.fixture
def get_user_credentials_by_user_id_factory(
    db_context: DBContext,
) -> GetUserCredentialsByUserIDFactory:
    return GetUserCredentialsByUserIDFactory(db_context)
