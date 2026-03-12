from datetime import timedelta

from pydantic import BaseModel, Field, field_validator

from shared.utils.datetime_utils import parse_simple_timedelta


class UserActionTokenConfig(BaseModel, frozen=True):
    short_token_length: int = 6
    long_token_bytes: int = 64
    expires_interval: timedelta = Field(
        default=timedelta(hours=24),
        description="Example: 30s, 5m, 2h, 7d.",
    )

    @field_validator("expires_interval", mode="before")
    @classmethod
    def parse_expires_interval(cls, value: object) -> object:
        if isinstance(value, str):
            return parse_simple_timedelta(value)
        return value
