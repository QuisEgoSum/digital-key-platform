from zoneinfo import available_timezones

from pydantic import BaseModel, field_validator

TZ_SET = available_timezones()


class I18NConfig(BaseModel, frozen=True):
    default_locale: str
    supported_locales: frozenset[str]


class TimezoneConfig(BaseModel, frozen=True):
    default_timezone: str

    @field_validator("default_timezone", mode="after")
    @classmethod
    def validate_default_timezone(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in TZ_SET:
            raise ValueError("Invalid timezone")
        return value


class RegionalConfig(BaseModel, frozen=True):
    i18n: I18NConfig
    timezone: TimezoneConfig
