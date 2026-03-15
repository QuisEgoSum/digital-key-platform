__all__ = (
    "UserFlowSessionAnyStorageDTO",
    "UserFlowSessionEmailVerificationDTO",
    "UserFlowSessionPasswordResetDTO",
    "UserSessionStorageDTO",
    "verify_user_flow_session",
    "verify_user_session",
)

import uuid

from typing import Literal, overload

from context.user.application.dtos.entity.user_flow_session import (
    UserFlowSessionAnyStorageDTO,
    UserFlowSessionEmailVerificationDTO,
    UserFlowSessionPasswordResetDTO,
)
from context.user.application.dtos.entity.user_session import (
    UserSessionStorageDTO,
)
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.services import (
    user_flow_session_service,
    user_session_service,
)


async def verify_user_session(
    *,
    session_id: uuid.UUID,
    secret: str,
) -> UserSessionStorageDTO:
    return await user_session_service.verify_session(
        session_id=session_id,
        secret=secret,
    )


@overload
async def verify_user_flow_session(
    *,
    session_id: uuid.UUID,
    secret: str,
    kind: Literal[UserFlowSessionKind.EMAIL_VERIFICATION],
) -> UserFlowSessionEmailVerificationDTO: ...


@overload
async def verify_user_flow_session(
    *,
    session_id: uuid.UUID,
    secret: str,
    kind: Literal[UserFlowSessionKind.PASSWORD_RESET],
) -> UserFlowSessionPasswordResetDTO: ...


@overload
async def verify_user_flow_session(
    *,
    session_id: uuid.UUID,
    kind: UserFlowSessionKind,
    secret: str,
) -> UserFlowSessionAnyStorageDTO: ...


async def verify_user_flow_session(
    *,
    session_id: uuid.UUID,
    kind: UserFlowSessionKind,
    secret: str,
) -> UserFlowSessionAnyStorageDTO:
    return await user_flow_session_service.verify_flow_session(
        session_id=session_id,
        kind=kind,
        secret=secret,
    )
