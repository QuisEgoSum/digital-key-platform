from typing import Any

from sanic import Sanic

from infra import openapi
from shared.utils.logger import get_logger

logger = get_logger(__name__)


async def before_server_start(_: Sanic[Any, Any]) -> None:
    logger.info("Starting server")


async def after_server_start(app: Sanic[Any, Any]) -> None:
    logger.info("Server successfully started")
    openapi.utils.collect(app)


async def before_server_stop(_: Sanic[Any, Any]) -> None:
    logger.info("Server shutting down")


async def after_server_stop(_: Sanic[Any, Any]) -> None:
    logger.info("Server successfully stopped")
