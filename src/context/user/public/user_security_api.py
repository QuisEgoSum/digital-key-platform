__all__ = (
    "AnySessionDTO",
    "AuthorizationSessionDTO",
    "PasswordResetSessionDTO",
    "UserSessionKind",
    "verify_session",
)

import uuid

from typing import Any, Literal, overload

from context.user.application.dtos.entity.user_session import (
    UserSessionPasswordResetStateDTO,
    UserSessionStorageDTO,
)
from context.user.application.enums.user_session import UserSessionKind
from context.user.application.services import user_session_service

AuthorizationSessionDTO = UserSessionStorageDTO[None]
PasswordResetSessionDTO = UserSessionStorageDTO[UserSessionPasswordResetStateDTO]
AnySessionDTO = UserSessionStorageDTO[Any]


@overload
async def verify_session(
    session_id: uuid.UUID,
    secret: str,
    kind: Literal[UserSessionKind.AUTHORIZATION, UserSessionKind.EMAIL_VERIFICATION],
) -> UserSessionStorageDTO[None]: ...


@overload
async def verify_session(
    session_id: uuid.UUID,
    secret: str,
    kind: Literal[UserSessionKind.PASSWORD_RESET],
) -> UserSessionStorageDTO[UserSessionPasswordResetStateDTO]: ...


@overload
async def verify_session(
    session_id: uuid.UUID,
    secret: str,
    kind: UserSessionKind,
) -> UserSessionStorageDTO[Any]: ...


async def verify_session(
    session_id: uuid.UUID,
    secret: str,
    kind: UserSessionKind,
) -> UserSessionStorageDTO[Any]:
    return await user_session_service.verify_session(
        session_id=session_id,
        secret=secret,
        kind=kind,
    )
