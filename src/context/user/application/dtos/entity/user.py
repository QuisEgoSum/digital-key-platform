from dataclasses import dataclass
from datetime import datetime
from functools import cached_property

from context.user.application.dtos.entity.user_credentials import UserCredentialsDTO
from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.enums.user import UserStatus


@dataclass(frozen=True)
class UserDTO:
    id: int

    name: str

    status: UserStatus
    status_until_at: datetime | None

    locale: str
    timezone: str

    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class UserMeDTO:
    id: int

    name: str

    locale: str
    timezone: str

    emails: list[UserEmailDTO]

    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class UserLoginDetailsDTO:
    id: int
    name: str
    status: UserStatus
    status_until_at: datetime | None
    locale: str
    timezone: str

    emails: list[UserEmailDTO]
    credentials: UserCredentialsDTO

    created_at: datetime
    updated_at: datetime

    @cached_property
    def primary_email(self) -> UserEmailDTO | None:
        for email in self.emails:
            if email.is_primary:
                return email

        return None

    @property
    def is_verified_primary_email(self) -> bool:
        return self.primary_email is not None and self.primary_email.is_verified
