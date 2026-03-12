from dataclasses import dataclass
from typing import TypeVar

from context.user.application.dtos.entity.user_session import UserSessionStorageDTO

T = TypeVar("T")


@dataclass(frozen=True)
class UserSessionCreateResult[T]:
    session_key: str
    storage: UserSessionStorageDTO[T]
