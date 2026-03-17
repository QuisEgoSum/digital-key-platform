from dataclasses import dataclass

import pytest

from context.user.application.dtos.data.user import UserCreateData
from context.user.application.dtos.entity.user import UserDTO
from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.services import (
    user_credentials_service,
    user_email_service,
    user_service,
)
from context.user.infra.models import UserRow
from infra.persistence.postgresql.connection import DBContext
from shared.utils.datetime_utils import current_datetime
from utils.query import BaseQuery


@dataclass()
class UserQuery(BaseQuery[UserRow, int]): ...


@pytest.fixture()
def user_query(db_context: DBContext) -> UserQuery:
    return UserQuery(db_context, UserRow, UserRow.id)


@dataclass()
class CreateUserResult:
    user: UserDTO
    email: UserEmailDTO


@dataclass()
class UserFactory:
    db: DBContext

    async def create(
        self,
        *,
        email: str = "user@example.com",
        password: str = "password",
        name: str = "User",
        locale: str = "en",
        timezone: str = "UTC",
        verify_email: bool = True,
    ) -> CreateUserResult:
        async with self.db.transaction():
            user = await user_service.create_user(
                UserCreateData(
                    name=name,
                    locale=locale,
                    timezone=timezone,
                ),
            )
            user_email = await user_email_service.create_user_email(
                user_id=user.id,
                email=email,
                is_primary=True,
                verified_at=current_datetime() if verify_email else None,
            )
            await user_credentials_service.create_user_credential(
                user_id=user.id,
                password=password,
            )

        return CreateUserResult(user=user, email=user_email)


@pytest.fixture()
def user_factory(db_context: DBContext) -> UserFactory:
    return UserFactory(db_context)
