from dataclasses import dataclass

from context.user.application.dtos.entity.user_session import UserSessionStorageDTO


@dataclass(frozen=True)
class UserSessionCreateResult:
    session_key: str
    storage: UserSessionStorageDTO
