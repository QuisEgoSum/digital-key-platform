"""User error codes: 2000-2009."""

from datetime import datetime

from shared.errors.base import AuthorizationError, NotFoundError


class UserNotFoundError(NotFoundError):
    message = "User not found."
    code = 2000


class UserBannedError(AuthorizationError):
    message = "User is banned."
    code = 2001


class UserTemporaryBlockedError(AuthorizationError):
    message = "User is temporary banned."
    code = 2002

    banned_until_at: datetime

    def __init__(self, banned_until_at: datetime):
        self.banned_until_at = banned_until_at

        super().__init__()
