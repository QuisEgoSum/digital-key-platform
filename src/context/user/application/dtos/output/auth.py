from typing import Literal

from pydantic import BaseModel

from context.user.application.dtos.entity.user import UserMeDTO
from context.user.application.types.auth import UserConfirmStatus, UserRegisterStatus


class UserRegisterOutput(BaseModel):
    status: UserRegisterStatus
    user: UserMeDTO | None = None


class UserLoginLoggedInOutput(BaseModel):
    status: Literal["logged_in"]
    user: UserMeDTO


class UserLoginEmailVerificationOutput(BaseModel):
    status: Literal["email_verification_required"]


class UserConfirmOutput(BaseModel):
    status: UserConfirmStatus
    user: UserMeDTO | None
