from collections.abc import Mapping
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator


class CookieDomainConfig(BaseModel, frozen=True):
    mode: Literal["host", "fixed", "allow_list"] = Field(
        default="host",
        description=(
            "Cookie domain selection mode: "
            "host - do not set the Domain attribute (host-only cookie); "
            "fixed - always set Domain to the value from 'fixed'; "
            "allow_list - set Domain only if the request host is present in 'allow_list'."
        ),
    )
    fixed: str | None = Field(
        default=None,
        description="Fixed Domain value to use when mode is 'fixed'.",
    )
    allow_list: frozenset[str] = Field(
        default_factory=frozenset,
        description="Allow-list of hosts/domains that are permitted for setting the Domain attribute.",
    )
    host_map: Mapping[str, str] = Field(
        default_factory=dict,
        description=(
            "Host-to-domain mapping rules. "
            "For example, 'app.example.com' -> '.example.com'. "
            "Used in the 'allow_list' mode."
        ),
    )

    @model_validator(mode="after")
    def move_conditions(self) -> Self:
        if self.mode == "fixed" and self.fixed is None:
            raise ValueError(
                "Field 'fixed' must be provided when cookie domain mode is 'fixed'.",
            )

        if self.mode == "allow_list" and not self.allow_list:
            raise ValueError(
                "Field 'allow_list' must not be empty when cookie domain mode is 'allow_list'.",
            )

        return self


class CookieDefaultsConfig(BaseModel, frozen=True):
    path: str = Field(
        default="/",
        description="Default Path attribute for cookies.",
    )
    secure: bool = Field(
        default=True,
        description="Default Secure attribute for cookies.",
    )
    httponly: bool = Field(
        default=True,
        description="Default HttpOnly attribute for cookies.",
    )
    samesite: Literal["Strict", "Lax", "None"] = Field(
        default="Lax",
        description="Default SameSite attribute for cookies.",
    )


class CookieDefaultsOverrideConfig(BaseModel, frozen=True):
    path: str | None = Field(
        default=None,
        description="Override Path attribute for cookies.",
    )
    secure: bool | None = Field(
        default=None,
        description="Override Secure attribute for cookies.",
    )
    httponly: bool | None = Field(
        default=None,
        description="Override HttpOnly attribute for cookies.",
    )
    samesite: Literal["Strict", "Lax", "None"] | None = Field(
        default=None,
        description="Override SameSite attribute for cookies.",
    )


class CookiePolicyConfig(BaseModel, frozen=True):
    domain: CookieDomainConfig = Field(
        default_factory=CookieDomainConfig,
        description="Cookie domain selection policy.",
    )
    defaults: CookieDefaultsConfig = Field(
        default_factory=CookieDefaultsConfig,
        description="Default cookie attributes applied when setting cookies.",
    )


class CookiePolicyOverrideConfig(BaseModel, frozen=True):
    domain: CookieDomainConfig | None = Field(
        default=None,
        description="Optional override for the domain selection policy.",
    )
    defaults: CookieDefaultsOverrideConfig | None = Field(
        default=None,
        description="Optional override for default cookie attributes.",
    )


class CookieConfig(BaseModel, frozen=True):
    name: str = Field(
        ...,
        description="Cookie name.",
    )
    max_age: int | None = Field(
        None,
        description="Max-Age in seconds.",
    )
    policy_override: CookiePolicyOverrideConfig | None = Field(
        default=None,
        description="Optional per-cookie override of the cookie policy.",
    )
