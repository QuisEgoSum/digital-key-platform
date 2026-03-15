from dataclasses import dataclass

from context.user.application.dtos.entity.user import UserMeDTO
from context.user.application.dtos.entity.user_flow_session import (
    UserFlowSessionEmailVerificationDTO,
    UserFlowSessionPasswordResetDTO,
)
from context.user.application.dtos.result.user_flow_session import (
    UserFlowSessionCreateResult,
)
from context.user.application.dtos.result.user_session import UserSessionCreateResult
from context.user.application.types.auth import UserLoginStatus, UserRegisterStatus


@dataclass(frozen=True)
class UserRegisterResult:
    flow_session: UserFlowSessionCreateResult[UserFlowSessionEmailVerificationDTO]
    status: UserRegisterStatus


@dataclass(frozen=True)
class UserLoginResult:
    user: UserMeDTO
    session: UserSessionCreateResult | None
    flow_session: (
        UserFlowSessionCreateResult[UserFlowSessionEmailVerificationDTO] | None
    )
    status: UserLoginStatus


@dataclass(frozen=True)
class UserConfirmEmailResult:
    auth_session: UserSessionCreateResult | None


@dataclass(frozen=True)
class UserConfirmPasswordResult:
    created_flow_session: (
        UserFlowSessionCreateResult[UserFlowSessionPasswordResetDTO] | None
    ) = None


@dataclass(frozen=True)
class UserRequestPasswordResetResult:
    created_flow_session: (
        UserFlowSessionCreateResult[UserFlowSessionPasswordResetDTO] | None
    ) = None
