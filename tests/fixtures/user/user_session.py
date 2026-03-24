import uuid

from dataclasses import dataclass

import pytest

from context.user.infra.models import UserSessionRow
from infra.persistence.postgresql.connection import DBContext
from utils.query import BaseQuery


@dataclass()
class UserSessionQuery(BaseQuery[UserSessionRow, uuid.UUID]): ...


@pytest.fixture()
def user_session_query(db_context: DBContext) -> UserSessionQuery:
    return UserSessionQuery(db_context, UserSessionRow, UserSessionRow.id)
