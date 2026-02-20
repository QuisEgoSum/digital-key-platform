from datetime import UTC, datetime


def current_datetime() -> datetime:
    return datetime.now(tz=UTC)
