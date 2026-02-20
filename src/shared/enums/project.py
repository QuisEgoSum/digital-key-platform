from enum import StrEnum


class ProjectServiceType(StrEnum):
    USER_HTTP = "user_http"
    ADMIN_HTTP = "admin_http"
    USER_WS = "user_ws"
    SCHEDULER = "scheduler"
    WEBHOOK_HTTP = "webhook_http"
