import pytest

from context.user.infra.models import UserActionTokenRow
from infra.persistence.postgresql.connection import DBContext
from utils.query import BaseQuery


class UserActionTokenQuery(BaseQuery[UserActionTokenRow, int]): ...


@pytest.fixture()
def user_action_token_query(db_context: DBContext) -> UserActionTokenQuery:
    return UserActionTokenQuery(db_context, UserActionTokenRow, UserActionTokenRow.id)
