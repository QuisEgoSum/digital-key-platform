import re

from datetime import UTC, datetime, timedelta

_DURATION_RE = re.compile(r"^(?P<value>\d+)(?P<unit>[smhd])$")


def current_datetime() -> datetime:
    return datetime.now(tz=UTC)


def parse_simple_timedelta(value: str | timedelta) -> timedelta:
    if isinstance(value, timedelta):
        return value

    if not isinstance(value, str):
        raise TypeError("Duration must be str or timedelta.")

    match = _DURATION_RE.fullmatch(value.strip())
    if not match:
        raise ValueError(
            "Invalid duration format. Expected formats like: 30s, 5m, 2h, 7d.",
        )

    amount = int(match.group("value"))
    unit = match.group("unit")

    if unit == "s":
        return timedelta(seconds=amount)
    if unit == "m":
        return timedelta(minutes=amount)
    if unit == "h":
        return timedelta(hours=amount)
    if unit == "d":
        return timedelta(days=amount)

    raise ValueError(f"Unsupported duration unit: {unit}")
