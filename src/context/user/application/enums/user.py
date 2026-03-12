from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "active"
    TEMPORARY_BLOCKED = "blocked"
    PERMANENT_BANNED = "banned"
    DELETED = "deleted"
