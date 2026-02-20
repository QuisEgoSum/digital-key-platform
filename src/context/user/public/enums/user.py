from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "active"
    TEMPORARY_BLOCKED = "blocked"
    PERMANENT_BANNED = "banned"
    DELETED = "deleted"


class UserSessionKind(StrEnum):
    AUTHORIZATION = "authorization"
    EMAIL_VERIFICATION = "email_verification"


class UserActionTokenKind(StrEnum):
    EMAIL_VERIFY = "email_verify"
    PASSWORD_RESET = "password_reset"


class UserActionTokenChannelType(StrEnum):
    EMAIL = "email"


class UserActionTokenStatusType(StrEnum):
    ACTIVE = "active"
    CANCELED = "canceled"
    USED = "used"
