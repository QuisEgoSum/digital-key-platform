import base64

from collections.abc import Callable, Coroutine, Mapping
from functools import wraps
from inspect import isawaitable
from typing import Any, ParamSpec, TypeVar, cast

from pydantic import SecretStr
from sanic import HTTPResponse, response as sanic_response

from infra import openapi
from infra.sanic.http.request import AppRequest
from shared.errors.authorization import UnauthorizedError

P = ParamSpec("P")
R = TypeVar("R")


def authorization_header_protected_factory(
    expected_token: str,
    security_name: str,
) -> Callable[[Callable[P, Any]], Callable[P, Any]]:
    def decorator(
        func: Callable[P, Any],
    ) -> Callable[P, Coroutine[Any, Any, HTTPResponse]]:
        @wraps(func)
        @openapi.security(security_name)
        @openapi.errors(UnauthorizedError)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> HTTPResponse:
            request = cast("AppRequest", args[0])
            received_token = request.headers.get("authorization")
            if received_token != expected_token:
                raise UnauthorizedError()
            response = func(*args, **kwargs)
            if isawaitable(response):
                response = await response
            return response

        return wrapper

    return decorator


def check_basic_auth(
    request: AppRequest,
    users: Mapping[str, SecretStr],
) -> bool:
    token = request.headers.get("authorization")

    if token is None or not token.startswith("Basic "):
        return False

    try:
        base64_credentials = base64.b64decode(token[6:].encode("UTF-8")).decode("UTF-8")
        username, password = base64_credentials.split(":", 1)

        if username not in users:
            return False
        return password == users[username].get_secret_value()
    except Exception:
        return False


def basic_auth_factory(
    users: Mapping[str, SecretStr],
    *,
    realm: str = "Access",
) -> Callable[[Callable[P, R | HTTPResponse]], Callable[P, R | HTTPResponse]]:
    def decorator(func: Callable[P, R | HTTPResponse]) -> Callable[P, R | HTTPResponse]:
        @openapi.security("BasicAuth")
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | HTTPResponse:
            request: AppRequest = cast("AppRequest", args[0])

            if not check_basic_auth(request, users):
                return sanic_response.empty(
                    401,
                    headers={"WWW-Authenticate": f'Basic realm="{realm}"'},
                )

            result = func(*args, **kwargs)
            if isawaitable(result):
                result = await result
            return result

        return wrapper  # type: ignore[return-value]

    return decorator
