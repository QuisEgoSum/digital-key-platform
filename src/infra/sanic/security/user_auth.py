import uuid

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, Concatenate, ParamSpec, TypeVar

from config import config
from context.user.application.dtos.entity.user_session import (
    UserSessionPasswordResetStateDTO,
    UserSessionStorageDTO,
)
from context.user.application.enums.user_session import UserSessionKind
from context.user.public import user_security_api
from infra import openapi
from infra.sanic.http.request import AppRequest
from shared.errors.authorization import UnauthorizedError

P = ParamSpec("P")
R = TypeVar("R")

AsyncRequestHandler = Callable[Concatenate[AppRequest, P], Awaitable[R]]

AuthorizationSessionDTO = UserSessionStorageDTO[None]
PasswordResetSessionDTO = UserSessionStorageDTO[UserSessionPasswordResetStateDTO]
AnySessionDTO = UserSessionStorageDTO[Any]


def require_user_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_session_loader(
        kind=UserSessionKind.AUTHORIZATION,
        require_session=True,
        inject_kwarg_name=None,
    )


def inject_user_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_session_loader(
        kind=UserSessionKind.AUTHORIZATION,
        require_session=True,
        inject_kwarg_name="session",
    )


def load_user_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_session_loader(
        kind=UserSessionKind.AUTHORIZATION,
        require_session=False,
        inject_kwarg_name=None,
    )


def require_email_verification_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_session_loader(
        kind=UserSessionKind.EMAIL_VERIFICATION,
        require_session=True,
        inject_kwarg_name=None,
    )


def inject_email_verification_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_session_loader(
        kind=UserSessionKind.EMAIL_VERIFICATION,
        require_session=True,
        inject_kwarg_name="session",
    )


def require_password_reset_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_session_loader(
        kind=UserSessionKind.PASSWORD_RESET,
        require_session=True,
        inject_kwarg_name=None,
    )


def inject_password_reset_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_session_loader(
        kind=UserSessionKind.PASSWORD_RESET,
        require_session=True,
        inject_kwarg_name="session",
    )


def load_password_reset_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_session_loader(
        kind=UserSessionKind.PASSWORD_RESET,
        require_session=False,
        inject_kwarg_name=None,
    )


def _build_session_loader(
    *,
    kind: UserSessionKind,
    require_session: bool,
    inject_kwarg_name: str | None = None,
) -> Callable[[AsyncRequestHandler[P, R]], AsyncRequestHandler[P, R]]:
    def decorator(func: AsyncRequestHandler[P, R]) -> AsyncRequestHandler[P, R]:
        security_name = _get_security_name(kind)
        cfg = config.context.user.get_cookie_config_by_kind(kind)

        if require_session:
            openapi.errors(UnauthorizedError)(func)

        @wraps(func)
        @openapi.security(security_name)
        async def wrapper(
            request: AppRequest,
            /,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R:
            session: AnySessionDTO | None = None
            session_key = request.cookies.get(cfg.name)

            if session_key is not None:
                try:
                    session_id, secret = _parse_session_key(session_key)
                    session = await user_security_api.verify_session(
                        session_id=session_id,
                        secret=secret,
                        kind=kind,
                    )
                except UnauthorizedError:
                    if require_session:
                        raise
            elif require_session:
                raise UnauthorizedError()

            request.ctx.session = session

            if inject_kwarg_name is not None:
                kwargs[inject_kwarg_name] = session

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def _get_security_name(kind: UserSessionKind) -> str:
    match kind:
        case UserSessionKind.AUTHORIZATION:
            return "UserSession"
        case UserSessionKind.PASSWORD_RESET:
            return "UserResetPasswordSession"
        case UserSessionKind.EMAIL_VERIFICATION:
            return "UserEmailVerificationSession"
        case _:
            raise ValueError(f"Unknown session kind {kind}")


def _parse_session_key(session_key: str) -> tuple[uuid.UUID, str]:
    try:
        raw_session_id, secret = session_key.split(":", 1)
        session_id = uuid.UUID(raw_session_id)
    except Exception as ex:
        raise UnauthorizedError() from ex

    if not secret:
        raise UnauthorizedError()

    return session_id, secret
