from dataclasses import dataclass

from context.user.application.enums.user import UserStatus


@dataclass(frozen=True, slots=True)
class UserCreatePayload:
    name: str
    locale: str
    timezone: str

    status: UserStatus = UserStatus.ACTIVE
