from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserCredentialsDTO:
    user_id: int
    password_hash: str | None
    password_changed_at: datetime
    created_at: datetime
    updated_at: datetime
