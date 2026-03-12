from enum import StrEnum


class UserActionTokenKind(StrEnum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class UserActionTokenChannelType(StrEnum):
    EMAIL = "email"


class UserActionTokenStatusType(StrEnum):
    ACTIVE = "active"
    CANCELED = "canceled"
    USED = "used"
