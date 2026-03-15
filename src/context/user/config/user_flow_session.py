from datetime import timedelta

from pydantic import BaseModel, field_validator

from shared.utils.datetime_utils import parse_simple_timedelta


class UserFlowSessionConfig(BaseModel, frozen=True):
    expires_interval: timedelta = timedelta(hours=6)

    @field_validator("expires_interval", mode="before")
    @classmethod
    def parse_expires_interval(cls, value: object) -> object:
        if isinstance(value, str):
            return parse_simple_timedelta(value)
        return value
