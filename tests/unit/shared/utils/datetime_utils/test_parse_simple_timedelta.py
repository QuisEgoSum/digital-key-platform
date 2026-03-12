from datetime import timedelta

from shared.utils.datetime_utils import parse_simple_timedelta


def test_parse_simple_timedelta() -> None:
    assert parse_simple_timedelta("1d") == timedelta(days=1)
    assert parse_simple_timedelta("1h") == timedelta(hours=1)
    assert parse_simple_timedelta("1m") == timedelta(minutes=1)
    assert parse_simple_timedelta("1s") == timedelta(seconds=1)
