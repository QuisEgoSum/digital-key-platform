from enum import StrEnum


class UserFlowSessionKind(StrEnum):
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
