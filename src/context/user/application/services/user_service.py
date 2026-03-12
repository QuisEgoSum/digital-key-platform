from context.user.application.dtos.entity.user import (
    UserDTO,
    UserLoginDetailsDTO,
    UserMeDTO,
)
from context.user.application.dtos.payload.user import UserCreatePayload
from context.user.application.enums.user import UserStatus
from context.user.application.errors.auth import InvalidCredentialsError
from context.user.application.errors.user import (
    UserBannedError,
    UserTemporaryBlockedError,
)
from context.user.infra.dao import user_dao


async def create_user(payload: UserCreatePayload) -> UserDTO:
    return await user_dao.insert_user(payload)


async def get_login_details(email: str) -> UserLoginDetailsDTO:
    login_details = await user_dao.get_login_details(email)
    if login_details is None:
        raise InvalidCredentialsError("user_not_found")
    return login_details


def verify_login_allowed(login_details: UserLoginDetailsDTO) -> None:
    match login_details.status:
        case UserStatus.DELETED:
            raise InvalidCredentialsError("user_deleted")
        case UserStatus.PERMANENT_BANNED:
            raise UserBannedError()
        case UserStatus.TEMPORARY_BLOCKED:
            if login_details.status_until_at is None:
                raise RuntimeError(
                    "User with TEMPORARY_BLOCKED must have status_until_at",
                )
            raise UserTemporaryBlockedError(
                banned_until_at=login_details.status_until_at,
            )


async def get_user_me(user_id: int) -> UserMeDTO:
    return await user_dao.get_user_me(user_id)
