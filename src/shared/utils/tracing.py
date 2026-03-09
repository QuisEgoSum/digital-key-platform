from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from opentelemetry.trace import Span, SpanKind, get_current_span, get_tracer
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


@contextmanager
def trace_span(
    name: str = "stub",
    kind: SpanKind = SpanKind.INTERNAL,
) -> Generator[Span, Any, Any]:
    tracer = get_tracer("app")
    with tracer.start_as_current_span(name, kind=kind) as span:
        yield span


def get_traces() -> tuple[str | None, str | None]:
    span = get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.trace_id:
        return format(ctx.trace_id, "032x"), format(ctx.span_id, "016x")
    return None, None


def get_trace_signature() -> str | None:
    """Human-readable trace identifier."""
    span = get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.trace_id:
        trace_id, span_id = format(ctx.trace_id, "032x"), format(ctx.span_id, "016x")
        return f"{trace_id}-{span_id}"
    return None


def get_traceparent() -> str | None:
    carrier: dict[str, str] = {}
    TraceContextTextMapPropagator().inject(carrier)
    traceparent = carrier.get("traceparent")
    return traceparent
