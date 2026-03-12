from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserEmailDTO:
    id: int

    user_id: int
    email: str

    is_primary: bool

    verified_at: datetime | None
    revoked_at: datetime | None

    created_at: datetime
    updated_at: datetime

    @property
    def is_verified(self) -> bool:
        return self.verified_at is not None

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None
