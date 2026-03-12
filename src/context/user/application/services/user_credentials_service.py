from context.user.application.dtos.entity.user import UserLoginDetailsDTO
from context.user.application.errors.auth import InvalidCredentialsError
from context.user.infra.dao import user_credentials_dao
from shared.security.hash import hash_password, verify_password


async def create_user_credential(
    user_id: int,
    password: str,
) -> None:
    await user_credentials_dao.insert_user_credentials(
        user_id=user_id,
        password_hash=hash_password(password),
    )


async def verify_user_credentials(
    login_details: UserLoginDetailsDTO,
    password: str,
) -> None:
    if login_details.credentials.password_hash is None:
        raise InvalidCredentialsError("unset_password")
    if not verify_password(
        plain_password=password,
        hashed_password=login_details.credentials.password_hash,
    ):
        raise InvalidCredentialsError("invalid_password")
