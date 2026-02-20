from _contextvars import Token
from contextlib import AbstractContextManager
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from opentelemetry.context import Context
from opentelemetry.trace import Span

from config.models.components.server import ServerConfig


@dataclass()
class AppSanicRequestCTX(SimpleNamespace):
    otel_token: Token[Context] | None = None
    start_timestamp: float | None = None
    request_id: str | None = None
    session: Any = None
    tracing_cm: AbstractContextManager[Span] | None = None


@dataclass()
class AppSanicCTX(SimpleNamespace):
    server_cfg: ServerConfig
