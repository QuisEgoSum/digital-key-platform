from dataclasses import dataclass
from datetime import datetime

from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
)


@dataclass(frozen=True)
class UserActionTokenInsertData:
    user_id: int
    kind: UserActionTokenKind
    channel: UserActionTokenChannelType
    channel_id: int

    short_token_hash: str
    long_token_hash: str

    expires_at: datetime
