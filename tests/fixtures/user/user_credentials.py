from dataclasses import dataclass

import pytest

from context.user.infra.models import UserCredentialsRow
from infra.persistence.postgresql.connection import DBContext
from utils.query import BaseQuery


@dataclass()
class UserCredentialsQuery(BaseQuery[UserCredentialsRow, int]): ...


@pytest.fixture()
def user_credentials_query(db_context: DBContext) -> UserCredentialsQuery:
    return UserCredentialsQuery(
        db_context,
        UserCredentialsRow,
        UserCredentialsRow.user_id,
    )
