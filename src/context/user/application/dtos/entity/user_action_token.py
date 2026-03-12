from dataclasses import dataclass
from datetime import datetime

from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
    UserActionTokenStatusType,
)
from shared.utils.datetime_utils import current_datetime


@dataclass(frozen=True)
class UserActionTokenDTO:
    id: int

    user_id: int
    kind: UserActionTokenKind
    status: UserActionTokenStatusType

    channel: UserActionTokenChannelType
    channel_id: int

    short_token_hash: str
    long_token_hash: str

    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    @property
    def is_expired(self) -> bool:
        return self.expires_at < current_datetime()


@dataclass(frozen=True)
class UserActionTokenGeneratedDTO:
    short_token: str
    long_token: str
    short_token_hash: str
    long_token_hash: str
