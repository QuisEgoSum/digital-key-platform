from dataclasses import dataclass

from context.user.application.dtos.entity.user import UserDTO, UserMeDTO
from context.user.application.dtos.result.user_session import UserSessionCreateResult
from context.user.application.types.auth import UserLoginStatus, UserRegisterStatus


@dataclass(frozen=True)
class UserRegisterResult:
    user: UserDTO
    session: UserSessionCreateResult[None]
    status: UserRegisterStatus


@dataclass(frozen=True)
class UserLoginResult:
    user: UserMeDTO
    session: UserSessionCreateResult[None]
    status: UserLoginStatus
