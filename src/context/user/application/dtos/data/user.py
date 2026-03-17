from dataclasses import dataclass

from context.user.application.enums.user import UserStatus


@dataclass(frozen=True, slots=True)
class UserCreateData:
    name: str
    locale: str
    timezone: str

    status: UserStatus = UserStatus.ACTIVE
