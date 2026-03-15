__all__ = (
    "UserAuthSessionDTO",
    "UserEmailVerificationSessionDTO",
    "UserFlowSessionAnyDTO",
    "UserPasswordResetSessionDTO",
    "inject_email_verification_session",
    "inject_password_reset_session",
    "inject_user_session",
    "load_email_verification_session",
    "load_password_reset_session",
    "load_user_session",
    "require_email_verification_session",
    "require_password_reset_session",
    "require_user_session",
)

import uuid

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TYPE_CHECKING, Concatenate, Literal, ParamSpec, TypeVar, overload

from config import config
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.public import user_security_api
from context.user.public.user_security_api import (
    UserFlowSessionAnyStorageDTO,
    UserFlowSessionEmailVerificationDTO,
    UserFlowSessionPasswordResetDTO,
    UserSessionStorageDTO,
)
from infra import openapi
from shared.errors.authorization import UnauthorizedError

type UserAuthSessionDTO = UserSessionStorageDTO
type UserEmailVerificationSessionDTO = UserFlowSessionEmailVerificationDTO
type UserPasswordResetSessionDTO = UserFlowSessionPasswordResetDTO
type UserFlowSessionAnyDTO = UserFlowSessionAnyStorageDTO

if TYPE_CHECKING:
    from infra.sanic.http.request import AppRequest


P = ParamSpec("P")
R = TypeVar("R")

AsyncRequestHandler = Callable[Concatenate["AppRequest", P], Awaitable[R]]


def require_user_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_user_session_loader(
        require_session=True,
        inject_kwarg_name=None,
    )


def inject_user_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_user_session_loader(
        require_session=True,
        inject_kwarg_name="session",
    )


def load_user_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_user_session_loader(
        require_session=False,
        inject_kwarg_name=None,
    )


def require_email_verification_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_user_flow_session_loader(
        kind=UserFlowSessionKind.EMAIL_VERIFICATION,
        require_session=True,
        inject_kwarg_name=None,
    )


def inject_email_verification_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_user_flow_session_loader(
        kind=UserFlowSessionKind.EMAIL_VERIFICATION,
        require_session=True,
        inject_kwarg_name="session",
    )


def load_email_verification_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_user_flow_session_loader(
        kind=UserFlowSessionKind.EMAIL_VERIFICATION,
        require_session=False,
        inject_kwarg_name=None,
    )


def require_password_reset_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_user_flow_session_loader(
        kind=UserFlowSessionKind.PASSWORD_RESET,
        require_session=True,
        inject_kwarg_name=None,
    )


def inject_password_reset_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_user_flow_session_loader(
        kind=UserFlowSessionKind.PASSWORD_RESET,
        require_session=True,
        inject_kwarg_name="session",
    )


def load_password_reset_session() -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]:
    return _build_user_flow_session_loader(
        kind=UserFlowSessionKind.PASSWORD_RESET,
        require_session=False,
        inject_kwarg_name=None,
    )


def _build_user_session_loader(
    *,
    require_session: bool,
    inject_kwarg_name: str | None,
) -> Callable[[AsyncRequestHandler[P, R]], AsyncRequestHandler[P, R]]:
    def decorator(func: AsyncRequestHandler[P, R]) -> AsyncRequestHandler[P, R]:
        cfg = config.context.user.authorization.cookie

        if require_session:
            openapi.errors(UnauthorizedError)(func)

        @wraps(func)
        @openapi.security("UserSession")
        async def wrapper(
            request: "AppRequest",
            /,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R:
            session: UserAuthSessionDTO | None = None
            session_key = request.cookies.get(cfg.name)

            if session_key is not None:
                try:
                    session_id, secret = _parse_session_key(session_key)
                    session = await user_security_api.verify_user_session(
                        session_id=session_id,
                        secret=secret,
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


@overload
def _build_user_flow_session_loader(
    *,
    kind: Literal[UserFlowSessionKind.EMAIL_VERIFICATION],
    require_session: bool,
    inject_kwarg_name: str | None,
) -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]: ...


@overload
def _build_user_flow_session_loader(
    *,
    kind: Literal[UserFlowSessionKind.PASSWORD_RESET],
    require_session: bool,
    inject_kwarg_name: str | None,
) -> Callable[
    [AsyncRequestHandler[P, R]],
    AsyncRequestHandler[P, R],
]: ...


def _build_user_flow_session_loader(
    *,
    kind: UserFlowSessionKind,
    require_session: bool,
    inject_kwarg_name: str | None,
) -> Callable[[AsyncRequestHandler[P, R]], AsyncRequestHandler[P, R]]:
    def decorator(func: AsyncRequestHandler[P, R]) -> AsyncRequestHandler[P, R]:
        cfg = config.context.user.get_flow_cookie_config_by_kind(kind)
        security_name = _get_user_flow_security_name(kind)

        if require_session:
            openapi.errors(UnauthorizedError)(func)

        @wraps(func)
        @openapi.security(security_name)
        async def wrapper(
            request: "AppRequest",
            /,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R:
            session: UserFlowSessionAnyDTO | None = None
            session_key = request.cookies.get(cfg.name)

            if session_key is not None:
                try:
                    session_id, secret = _parse_session_key(session_key)
                    session = await user_security_api.verify_user_flow_session(
                        session_id=session_id,
                        secret=secret,
                        kind=kind,
                    )
                except UnauthorizedError:
                    if require_session:
                        raise
            elif require_session:
                raise UnauthorizedError()

            request.ctx.flow_session = session

            if inject_kwarg_name is not None:
                kwargs[inject_kwarg_name] = session

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def _get_user_flow_security_name(kind: UserFlowSessionKind) -> str:
    match kind:
        case UserFlowSessionKind.EMAIL_VERIFICATION:
            return "UserEmailVerificationSession"
        case UserFlowSessionKind.PASSWORD_RESET:
            return "UserPasswordResetSession"
        case _:
            raise ValueError(f"Unknown user flow session kind: {kind}")


def _parse_session_key(session_key: str) -> tuple[uuid.UUID, str]:
    try:
        raw_session_id, secret = session_key.split(":", 1)
        session_id = uuid.UUID(raw_session_id)
    except Exception as ex:
        raise UnauthorizedError() from ex

    if not secret:
        raise UnauthorizedError()

    return session_id, secret
