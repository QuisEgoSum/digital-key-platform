from pydantic import BaseModel, SecretStr

from context.user.application.dtos.entity.user_flow_session import (
    UserFlowSessionEmailVerificationDTO,
    UserFlowSessionPasswordResetDTO,
)
from context.user.application.dtos.entity.user_session import (
    UserSessionStorageDTO,
)


class UserRegisterCommand(BaseModel, frozen=True):
    name: str
    email: str
    password: SecretStr
    timezone: str
    locale: str
    ip_address: str | None


class UserLoginCommand(BaseModel, frozen=True):
    email: str
    password: SecretStr
    ip_address: str | None


class UserLogoutCommand(BaseModel, frozen=True):
    session: UserSessionStorageDTO
    ip_address: str | None


class UserRequestConfirmEmailCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionEmailVerificationDTO
    ip_address: str | None


class UserConfirmEmailByCodeCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionEmailVerificationDTO
    token: str
    ip_address: str | None


class UserConfirmEmailByLinkCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionEmailVerificationDTO | None
    token: str
    ip_address: str | None


class UserConfirmPasswordByCodeCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionPasswordResetDTO
    token: str
    ip_address: str | None


class UserConfirmPasswordByLinkCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionPasswordResetDTO | None
    token: str
    ip_address: str | None


class UserRequestPasswordResetCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionPasswordResetDTO | None
    email: str
    ip_address: str | None


class UserPasswordResetCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionPasswordResetDTO
    password: SecretStr
    ip_address: str | None
