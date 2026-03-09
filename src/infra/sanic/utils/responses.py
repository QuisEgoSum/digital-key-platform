from collections.abc import MutableMapping
from typing import Any

from sanic import HTTPResponse, response as sanic_response
from sanic.response import JSONResponse

from infra.http.cookie.builder import build_cookie_delete, build_cookie_set
from infra.http.cookie.config import CookieConfig, CookiePolicyConfig
from infra.sanic.http.request import AppRequest
from shared.serialization.json import strict_orjson_dumps
from shared.utils.logger import get_logger
from shared.utils.tracing import get_traceparent

logger = get_logger(__name__)


def json_response(
    body: Any,
    status: int = 200,
    headers: dict[str, str] | None = None,
    content_type: str = "application/json",
    **kwargs: Any,
) -> JSONResponse:
    return sanic_response.json(
        body,
        status=status,
        headers=headers,
        content_type=content_type,
        dumps=strict_orjson_dumps,
        **kwargs,
    )


def build_response_headers(request: AppRequest) -> MutableMapping[str, str]:
    headers: MutableMapping[str, str] = {}

    traceparent = get_traceparent()

    if traceparent:
        # https://www.w3.org/TR/trace-context/
        headers["traceparent"] = traceparent

    if request.ctx.request_id:
        headers["X-Request-Id"] = request.ctx.request_id

    return headers


def add_cookie(
    response: HTTPResponse,
    *,
    cookie: CookieConfig,
    value: str,
    server_policy: CookiePolicyConfig,
    request_host: str,
) -> None:
    cookie_set = build_cookie_set(
        cookie=cookie,
        value=value,
        server_policy=server_policy,
        request_host=request_host,
    )

    logger.debug(
        "Set cookie",
        cookie=cookie_set,
    )

    response.add_cookie(
        cookie_set.name,
        cookie_set.value,
        path=cookie_set.path,
        max_age=cookie_set.max_age,
        domain=cookie_set.domain,
        samesite=cookie_set.samesite,
        secure=cookie_set.secure,
    )


def delete_cookie(
    response: HTTPResponse,
    *,
    cookie: CookieConfig,
    server_policy: CookiePolicyConfig,
    request_host: str,
) -> None:
    cookie_delete = build_cookie_delete(
        cookie=cookie,
        server_policy=server_policy,
        request_host=request_host,
    )

    logger.debug(
        "Delete cookie",
        cookie=cookie_delete,
    )

    response.delete_cookie(
        cookie_delete.name,
        path=cookie_delete.path,
        domain=cookie_delete.domain,
    )
