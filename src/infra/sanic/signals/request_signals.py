import time
import uuid

from typing import Any

from opentelemetry import context, trace
from opentelemetry.propagate import extract
from sanic import Sanic

from infra.sanic.http.request import AppRequest


def register_request_signals(app: Sanic[Any, Any]) -> None:
    tracer = trace.get_tracer(__name__)

    @app.signal("http.lifecycle.request", priority=98)
    async def add_start_timestamp(request: AppRequest) -> None:
        request.ctx.start_timestamp = time.monotonic()

    # noinspection PyUnusedLocal
    @app.signal("http.lifecycle.request", priority=97)
    async def tracing_request_handler(
        request: AppRequest,
    ) -> None:
        request.ctx.otel_token = context.attach(extract(request.headers))

        span_name = f"{request.method} {request.path}"

        span_cm = tracer.start_as_current_span(span_name, kind=trace.SpanKind.SERVER)
        request.ctx.tracing_cm = span_cm
        request.ctx.tracing_cm.__enter__()

    @app.signal("http.lifecycle.request", priority=96)
    async def request_id_handler(request: AppRequest) -> None:
        request_id = request.headers.get("X-REQUEST-ID") or str(uuid.uuid4())
        request.ctx.request_id = request_id
