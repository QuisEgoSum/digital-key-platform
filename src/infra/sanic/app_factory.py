from typing import TYPE_CHECKING, cast

from sanic import Config, Request, Sanic

from config.models.components.server import ServerConfig
from infra.sanic import listeners
from infra.sanic.ctx import AppSanicCTX
from infra.sanic.hooks.exception_handler import register_exception_handler
from infra.sanic.http.request import AppRequest
from infra.sanic.openapi.handler import router as openapi_router
from infra.sanic.signals.request_signals import register_request_signals
from infra.sanic.signals.response_signals import register_response_signals
from infra.sanic.types import AppSanic
from shared.enums.project import ProjectServiceType

if TYPE_CHECKING:
    from types import SimpleNamespace


def app_factory(
    service: ProjectServiceType,
    server_cfg: ServerConfig,
) -> AppSanic:
    app = Sanic(
        service.name,
        configure_logging=False,
        request_class=cast(
            "type[Request[Sanic[Config, SimpleNamespace], SimpleNamespace]]",
            AppRequest,
        ),
        ctx=AppSanicCTX(
            server_cfg=server_cfg,
        ),
    )

    app.blueprint(openapi_router)

    register_exception_handler(app)

    app.register_listener(listeners.before_server_start, "before_server_start")
    app.register_listener(listeners.after_server_start, "after_server_start")
    app.register_listener(listeners.before_server_stop, "before_server_stop")
    app.register_listener(listeners.after_server_stop, "after_server_stop")

    register_request_signals(app)
    register_response_signals(app)

    return app
