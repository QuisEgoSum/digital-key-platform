from contextlib import AbstractContextManager
from contextvars import Token
from dataclasses import dataclass
from types import SimpleNamespace

from opentelemetry.context import Context
from opentelemetry.trace import Span

from config.models.components.server import ServerConfig
from config.models.root import AppConfig
from infra.sanic.security.user_auth import UserAuthSessionDTO, UserFlowSessionAnyDTO


@dataclass()
class AppSanicRequestCTX(SimpleNamespace):
    otel_token: Token[Context] | None = None
    start_timestamp: float | None = None
    request_id: str | None = None
    session: UserAuthSessionDTO | None = None
    flow_session: UserFlowSessionAnyDTO | None = None
    tracing_cm: AbstractContextManager[Span] | None = None


@dataclass()
class AppSanicCTX(SimpleNamespace):
    server_config: ServerConfig
    config: AppConfig
