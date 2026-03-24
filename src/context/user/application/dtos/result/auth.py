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
from context.user.application.types.auth import (
    UserConfirmStatus,
    UserLoginStatus,
    UserRegisterStatus,
)


@dataclass(frozen=True)
class UserRegisterResult:
    auth_session: UserSessionCreateResult | None
    flow_session: UserFlowSessionCreateResult[UserFlowSessionEmailVerificationDTO]
    status: UserRegisterStatus
    user: UserMeDTO | None


@dataclass(frozen=True)
class UserLoginResult:
    user: UserMeDTO
    auth_session: UserSessionCreateResult | None
    flow_session: (
        UserFlowSessionCreateResult[UserFlowSessionEmailVerificationDTO] | None
    )
    status: UserLoginStatus


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


@dataclass(frozen=True)
class UserPasswordResetResult:
    auth_session: UserSessionCreateResult | None


@dataclass(frozen=True)
class UserActionConfirmResult:
    status: UserConfirmStatus
    user_me: UserMeDTO | None
    auth_session: UserSessionCreateResult | None
