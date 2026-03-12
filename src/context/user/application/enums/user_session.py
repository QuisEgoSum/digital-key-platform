from enum import StrEnum


class UserSessionKind(StrEnum):
    AUTHORIZATION = "authorization"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
