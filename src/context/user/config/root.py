from typing import Final

from pydantic import BaseModel, Field, model_validator

from context.user.application.enums.user_action_token import UserActionTokenKind
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.config.user_action_token import UserActionTokenConfig
from context.user.config.user_flow_session import UserFlowSessionConfig
from context.user.config.user_session import UserSessionConfig
from infra.http.cookie.config import CookieConfig

DEFAULT_COOKIE_MAX_AGE: Final[int] = 5184000000


class UserAuthorizationConfig(BaseModel, frozen=True):
    session: UserSessionConfig = Field(default_factory=UserSessionConfig)
    cookie: CookieConfig = Field(
        default_factory=lambda: CookieConfig(
            name="session",
            max_age=DEFAULT_COOKIE_MAX_AGE,
        ),
    )
    login_requires_verified_email: bool = Field(
        True,
        description="If True, user must verify email before login is allowed.",
    )
    hide_email_existence_on_register: bool = Field(
        True,
        description="If True, prevents account enumeration by returning the same response "
        "when registering an already existing email.",
    )

    @model_validator(mode="after")
    def validate_flags(self) -> "UserAuthorizationConfig":
        if (
            not self.login_requires_verified_email
            and self.hide_email_existence_on_register
        ):
            raise ValueError(
                "hide_email_existence_on_register=True requires "
                "login_requires_verified_email=True",
            )
        return self


class UserEmailVerificationConfig(BaseModel, frozen=True):
    session: UserFlowSessionConfig = Field(
        default_factory=UserFlowSessionConfig,
    )
    cookie: CookieConfig = Field(
        default_factory=lambda: CookieConfig(
            name="ev_session",
            max_age=DEFAULT_COOKIE_MAX_AGE,
        ),
    )
    token: UserActionTokenConfig = Field(
        default_factory=UserActionTokenConfig,
    )
    auto_login_on_success: bool = Field(
        False,
        description="Automatically authorize the user after successful completion of the flow..",
    )


class UserResetPasswordConfig(BaseModel, frozen=True):
    session: UserFlowSessionConfig = Field(
        default_factory=UserFlowSessionConfig,
    )
    cookie: CookieConfig = Field(
        default_factory=lambda: CookieConfig(
            name="rp_session",
            max_age=DEFAULT_COOKIE_MAX_AGE,
        ),
    )
    token: UserActionTokenConfig = Field(
        default_factory=UserActionTokenConfig,
    )
    auto_login_on_success: bool = Field(
        True,
        description="Automatically authorize the user after successful completion of the flow..",
    )
    hide_email_existence_on_request: bool = Field(
        True,
        description="If True, prevents account enumeration by returning the same response for existing "
        "and non-existing emails when requesting a password reset.",
    )


class UserConfig(BaseModel, frozen=True):
    authorization: UserAuthorizationConfig = Field(
        default_factory=UserAuthorizationConfig,
    )
    email_verification: UserEmailVerificationConfig = Field(
        default_factory=UserEmailVerificationConfig,
    )
    password_reset: UserResetPasswordConfig = Field(
        default_factory=UserResetPasswordConfig,
    )

    def get_token_config_by_kind(
        self,
        kind: UserActionTokenKind,
    ) -> UserActionTokenConfig:
        match kind:
            case UserActionTokenKind.EMAIL_VERIFICATION:
                return self.email_verification.token
            case UserActionTokenKind.PASSWORD_RESET:
                return self.password_reset.token
            case _:
                raise ValueError(f"Unsupported token kind: {kind!r}")

    def get_flow_session_config_by_kind(
        self,
        kind: UserFlowSessionKind,
    ) -> UserFlowSessionConfig:
        match kind:
            case UserFlowSessionKind.EMAIL_VERIFICATION:
                return self.email_verification.session
            case UserActionTokenKind.PASSWORD_RESET:
                return self.password_reset.session
            case _:
                raise ValueError(f"Unsupported flow session kind: {kind!r}")

    def get_flow_cookie_config_by_kind(self, kind: UserFlowSessionKind) -> CookieConfig:
        match kind:
            case UserFlowSessionKind.EMAIL_VERIFICATION:
                return self.email_verification.cookie
            case UserActionTokenKind.PASSWORD_RESET:
                return self.password_reset.cookie
            case _:
                raise ValueError(f"Unsupported flow session kind: {kind!r}")
