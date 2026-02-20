import time

from typing import Any

from opentelemetry import context
from sanic import HTTPResponse, Sanic

from infra.sanic.http.request import AppRequest
from infra.sanic.utils.request import get_request_ip_address
from infra.sanic.utils.responses import build_response_headers
from shared.utils.logger import get_logger

sanic_access_logger = get_logger("infra.sanic.access")


def register_response_signals(app: Sanic[Any, Any]) -> None:
    @app.signal("http.lifecycle.response", priority=99)
    async def request_id_handler(
        request: AppRequest,
        response: HTTPResponse,
    ) -> None:
        # TODO: Stream Response
        response.headers.update(build_response_headers(request))

    @app.signal("http.lifecycle.response", priority=98)
    async def access_log_handler(
        request: AppRequest,
        response: HTTPResponse,
    ) -> None:
        additional_log_parameters: dict[str, str | int | float | None] = {
            "request_id": request.ctx.request_id,
        }

        if request.ctx.start_timestamp:
            additional_log_parameters["time"] = (
                time.monotonic() - request.ctx.start_timestamp
            )

        if request.ctx.session:
            additional_log_parameters["session_id"] = request.ctx.session.session_id
            additional_log_parameters["user_id"] = request.ctx.session.user_id

        sanic_access_logger.info(
            "Sanic access",
            host=request.host,
            method=request.method,
            request=request.path,
            req_byte=len(request.body),
            res_byte=len(response.body) if response.body else 0,
            ip=get_request_ip_address(request),
            status=response.status,
            **additional_log_parameters,
        )

    @app.signal("http.lifecycle.response", priority=1)
    async def tracing_close_handler(
        request: AppRequest,
        response: HTTPResponse,  # noqa: ARG001
    ) -> None:
        if request.ctx.otel_token:
            context.detach(request.ctx.otel_token)

        if request.ctx.tracing_cm:
            request.ctx.tracing_cm.__exit__(None, None, None)
