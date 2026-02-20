from typing import Any

from sanic import Sanic
from sanic.worker.loader import AppLoader

from config import config
from context.user.entrypoint.user_http.router import router as user_router
from infra import openapi
from infra.openapi import setup
from infra.sanic.app_factory import app_factory
from shared.runtime.process import set_linux_proc_name


def main() -> None:
    set_linux_proc_name("dkp:capi")
    start_server()


def create_app() -> Sanic[Any, Any]:
    app = app_factory(
        service=config.project.service,
        server_cfg=config.entrypoint.user_http.server,
    )

    app.register_listener(before_server_start, "before_server_start")

    app.blueprint(user_router)

    return app


def start_server() -> None:
    cfg = config.entrypoint.user_http.server

    loader = AppLoader(factory=create_app)

    app = loader.load()

    app.prepare(
        host=cfg.host,
        port=cfg.port,
        workers=cfg.workers,
        access_log=False,
    )

    Sanic.serve(primary=app, app_loader=loader)


def setup_openapi() -> None:
    cfg = config.entrypoint.user_http.server

    openapi_spec = openapi.utils.get_raw_openapi()

    openapi_spec["components"] = {
        "securitySchemes": {
            "UserSession": {
                "type": "apiKey",
                "name": cfg,
                "in": "cookie",
            },
        },
    }
    openapi_spec["x-tagGroups"] = [
        {"name": "User", "tags": ["User"]},
    ]
    openapi_spec["servers"].append({"url": cfg.url})

    setup.setup_openapi(config.project)


def before_server_start(_: Sanic[Any, Any]) -> None:
    set_linux_proc_name("dkp:capi:w")
    setup_openapi()
