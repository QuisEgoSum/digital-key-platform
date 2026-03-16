from datetime import datetime

from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.errors.user_email import UserEmailNotFoundError
from context.user.infra.dao import user_email_dao
from shared.utils.datetime_utils import current_datetime


async def create_user_email(
    user_id: int,
    email: str,
    is_primary: bool,
    verified_at: datetime | None = None,
) -> UserEmailDTO:
    return await user_email_dao.insert_user_email(
        user_id=user_id,
        email=email,
        is_primary=is_primary,
        verified_at=verified_at,
    )


async def verify_email(email_id: int) -> UserEmailDTO:
    user_email = await user_email_dao.set_verified_at(
        email_id,
        verified_at=current_datetime(),
    )

    if user_email is None:
        raise UserEmailNotFoundError()

    return user_email


async def get_user_primary_email(user_id: int) -> UserEmailDTO:
    user_email = await user_email_dao.get_user_primary_email(user_id)

    if user_email is None:
        raise UserEmailNotFoundError()

    return user_email


async def get_email(email: str) -> UserEmailDTO:
    user_email = await user_email_dao.get_email(email)

    if user_email is None:
        raise UserEmailNotFoundError()

    return user_email
