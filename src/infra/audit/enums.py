from enum import StrEnum


class AuditActorType(StrEnum):
    ADMIN = "admin"
    USER = "user"
    SYSTEM = "system"
    EXTERNAL_API = "external_api"


class AuditSubjectType(StrEnum):
    USER = "user"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class AuditActionType(StrEnum):
    USER_SUCCESS_LOGIN = "user_success_login"
    USER_FAILED_LOGIN = "user_failed_login"


class AuditEventEntityRoleType(StrEnum):
    RECIPIENT = "recipient"
    ORIGIN = "origin"
    OWNER = "owner"
    CONTEXT = "context"
    SOURCE = "source"
    TARGET = "target"
    RELATED = "related"
