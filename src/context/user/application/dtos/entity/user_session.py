import uuid

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserSessionDTO:
    id: uuid.UUID

    user_id: int
    created_ip: str
    is_deleted: bool
    created_at: datetime


@dataclass(frozen=True)
class UserSessionStorageDTO:
    session_id: uuid.UUID
    user_id: int
    secret_hash: str
