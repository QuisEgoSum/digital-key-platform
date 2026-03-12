import uuid

from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar

from context.user.application.enums.user_session import UserSessionKind

T = TypeVar("T")


@dataclass(frozen=True)
class UserSessionDTO:
    id: uuid.UUID

    kind: UserSessionKind
    user_id: int
    created_ip: str
    is_deleted: bool
    created_at: datetime


@dataclass()
class UserSessionPasswordResetStateDTO:
    is_confirmed: bool = False


@dataclass(frozen=True)
class UserSessionStorageDTO[T]:
    session_id: uuid.UUID
    user_id: int
    kind: UserSessionKind
    state: T
    secret_hash: str
