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
    ip_address: str


class UserLoginCommand(BaseModel, frozen=True):
    email: str
    password: SecretStr
    ip_address: str


class UserLogoutCommand(BaseModel, frozen=True):
    session: UserSessionStorageDTO
    ip_address: str


class UserRequestConfirmEmailCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionEmailVerificationDTO
    ip_address: str


class UserConfirmEmailByCodeCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionEmailVerificationDTO
    token: str
    ip_address: str


class UserConfirmEmailByLinkCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionEmailVerificationDTO
    token: str
    ip_address: str


class UserConfirmPasswordByCodeCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionPasswordResetDTO
    token: str
    ip_address: str


class UserConfirmPasswordByLinkCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionPasswordResetDTO | None
    token: str
    ip_address: str


class UserRequestPasswordResetCommand(BaseModel, frozen=True):
    flow_session: UserFlowSessionPasswordResetDTO | None
    email: str
    ip_address: str
