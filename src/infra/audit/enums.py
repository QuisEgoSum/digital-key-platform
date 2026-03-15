from enum import StrEnum


class AuditActorType(StrEnum):
    ADMIN = "admin"
    USER = "user"
    ANONYMOUS = "anonymous"
    SYSTEM = "system"
    EXTERNAL_SERVICE = "external_service"


class AuditSubjectType(StrEnum):
    USER = "user"
    USER_ACTION_TOKEN = "user_action_token"
    USER_SESSION = "user_session"
    USER_EMAIL = "user_email"


class AuditScopeType(StrEnum):
    USER = "user"
    ADMIN = "admin"


class AuditEntityType(StrEnum):
    USER = "user"
    USER_EMAIL = "user_email"
    USER_ACTION_TOKEN = "user_action_token"
    USER_SESSION = "user_session"
    USER_FLOW_SESSION = "user_flow_session"


class AuditActionType(StrEnum):
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    EMAIL_VERIFICATION_REQUEST = "email_verification_request"
    EMAIL_VERIFICATION_CONFIRM = "email_verification_confirm"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_CONFIRM = "password_reset_confirm"
    PASSWORD_CHANGE = "password_change"


class AuditResultType(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    REJECTED = "rejected"


class AuditEventEntityRoleType(StrEnum):
    RECIPIENT = "recipient"
    ORIGIN = "origin"
    OWNER = "owner"
    CONTEXT = "context"
    SOURCE = "source"
    TARGET = "target"
    RELATED = "related"
    RESULT = "result"
    FLOW = "flow"
