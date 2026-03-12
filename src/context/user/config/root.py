from typing import Final

from pydantic import BaseModel, Field

from context.user.application.enums.user_action_token import UserActionTokenKind
from context.user.application.enums.user_session import UserSessionKind
from context.user.config.user_action_token import UserActionTokenConfig
from context.user.config.user_session import UserSessionConfig
from infra.http.cookie.config import CookieConfig

DEFAULT_COOKIE_MAX_AGE: Final[int] = 5184000000


class UserAuthorizationConfig(BaseModel, frozen=True):
    session: UserSessionConfig = Field(default_factory=UserSessionConfig)
    cookie: CookieConfig = Field(
        default_factory=lambda: CookieConfig(
            name="session_id",
            max_age=DEFAULT_COOKIE_MAX_AGE,
        ),
    )


class UserEmailVerificationConfig(BaseModel, frozen=True):
    session: UserSessionConfig = Field(
        default_factory=lambda: UserSessionConfig(auto_renewal=False),
    )
    cookie: CookieConfig = Field(
        default_factory=lambda: CookieConfig(
            name="ev_session_id",
            max_age=DEFAULT_COOKIE_MAX_AGE,
        ),
    )
    token: UserActionTokenConfig = Field(
        default_factory=UserActionTokenConfig,
    )


class UserResetPasswordConfig(BaseModel, frozen=True):
    session: UserSessionConfig = Field(
        default_factory=lambda: UserSessionConfig(
            active_session_limit=1,
            auto_renewal=False,
        ),
    )
    cookie: CookieConfig = Field(
        default_factory=lambda: CookieConfig(
            name="rp_session_id",
            max_age=DEFAULT_COOKIE_MAX_AGE,
        ),
    )
    token: UserActionTokenConfig = Field(
        default_factory=UserActionTokenConfig,
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

        raise ValueError(f"Unsupported token kind: {kind!r}")

    def get_session_config_by_kind(
        self,
        kind: UserSessionKind,
    ) -> UserSessionConfig:
        match kind:
            case UserSessionKind.AUTHORIZATION:
                return self.authorization.session
            case UserSessionKind.EMAIL_VERIFICATION:
                return self.email_verification.session
            case UserSessionKind.PASSWORD_RESET:
                return self.password_reset.session

        raise ValueError(f"Unsupported session kind: {kind!r}")

    def get_cookie_config_by_kind(self, kind: UserSessionKind) -> CookieConfig:
        match kind:
            case UserSessionKind.AUTHORIZATION:
                return self.authorization.cookie
            case UserSessionKind.EMAIL_VERIFICATION:
                return self.email_verification.cookie
            case UserSessionKind.PASSWORD_RESET:
                return self.password_reset.cookie

        raise ValueError(f"Unsupported session kind: {kind!r}")
