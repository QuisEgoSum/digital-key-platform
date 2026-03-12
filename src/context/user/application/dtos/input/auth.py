from zoneinfo import available_timezones

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator

TZ_SET = available_timezones()


class UserPreferencesInput(BaseModel, frozen=True):
    timezone: str | None = Field(
        None,
        description="`Intl.DateTimeFormat().resolvedOptions().timeZone`",
    )
    locale: str | None = Field(
        None,
    )

    @field_validator("timezone", mode="after")
    @classmethod
    def validate_timezone(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in TZ_SET:
            raise ValueError("Invalid timezone")
        return value


class UserRegisterInput(UserPreferencesInput, frozen=True):
    name: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )
    email: EmailStr = Field(
        ...,
        max_length=320,
    )
    password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserLoginInput(BaseModel, frozen=True):
    email: EmailStr = Field(
        ...,
        max_length=320,
    )
    password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()
