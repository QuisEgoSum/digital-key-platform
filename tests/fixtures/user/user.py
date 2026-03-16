from collections.abc import Sequence
from dataclasses import dataclass

import pytest

from sqlalchemy import select

from context.user.application.dtos.entity.user import UserDTO
from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.dtos.payload.user import UserCreatePayload
from context.user.application.services import (
    user_credentials_service,
    user_email_service,
    user_service,
)
from context.user.infra.models import UserRow
from infra.persistence.postgresql.connection import DBContext
from shared.utils.datetime_utils import current_datetime


@dataclass()
class CreateUserResult:
    user: UserDTO
    email: UserEmailDTO


@dataclass()
class CreateUserFactory:
    db: DBContext

    async def __call__(
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
                UserCreatePayload(
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
def create_user_factory(db_context: DBContext) -> CreateUserFactory:
    return CreateUserFactory(db_context)


@dataclass()
class GetUserByIdFactory:
    db: DBContext

    async def __call__(self, user_id: int) -> UserRow:
        async with self.db.session():
            stmt = select(UserRow).where(UserRow.id == user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one()


@pytest.fixture()
def get_user_by_id_factory(db_context: DBContext) -> GetUserByIdFactory:
    return GetUserByIdFactory(db_context)


@dataclass()
class GetUsersFactory:
    db: DBContext

    async def __call__(self) -> Sequence[UserRow]:
        async with self.db.session():
            stmt = select(UserRow)
            result = await self.db.execute(stmt)
            return result.scalars().all()


@pytest.fixture()
def get_users_factory(db_context: DBContext) -> GetUsersFactory:
    return GetUsersFactory(db_context)
