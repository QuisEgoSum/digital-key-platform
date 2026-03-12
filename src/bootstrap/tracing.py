from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


def setup_tracer() -> None:
    """Initializes a simple TracerProvider without exporters.

    Used for logging trace_id/span_id.
    """
    trace.set_tracer_provider(TracerProvider())
