from collections.abc import Callable
from typing import Any, TypeVar

from sanic import response
from sanic.exceptions import RequestCancelled, SanicException
from sanic.response import HTTPResponse, JSONResponse
from websockets import InvalidUpgrade

from infra.http.adapters.exception_to_http import get_http_status
from infra.http.errors import InternalServerError
from infra.sanic.http.request import AppRequest
from infra.sanic.types import AppSanic
from infra.sanic.validator.errors import SchemaValidationError
from shared.errors.base import ApplicationError
from shared.utils.logger import get_logger

logger = get_logger(__name__)


F = TypeVar("F", bound=Callable[..., Any])


def register_exception_handler(app: AppSanic) -> None:
    internal_server_error_dict = InternalServerError().to_dict()

    @app.exception(SchemaValidationError)
    def validation_exception_handler(
        _: AppRequest,
        exception: SchemaValidationError,
    ) -> JSONResponse:
        return response.json(exception.to_dict(), status=400)

    @app.exception(SanicException)
    def sanic_exception_handler(
        _: AppRequest,
        exception: SanicException,
    ) -> JSONResponse:
        if exception.status_code < 500:
            logger.warning(
                "Sanic error",
                error=str(exception),
                error_cls=str(type(exception)),
                status_code=exception.status_code,
            )
        else:
            logger.error(
                "Sanic error",
                error=str(exception),
                error_cls=str(type(exception)),
                status_code=exception.status_code,
                exc_info=(type(exception), exception, exception.__traceback__),
            )
        return response.json({"message": str(exception)}, status=exception.status_code)

    @app.exception(ApplicationError)
    def application_exception_handler(
        _: AppRequest,
        exception: ApplicationError,
    ) -> JSONResponse:
        payload = exception.to_dict()
        status_code = get_http_status(exception)
        logger.warning(
            "Application error",
            error=payload,
            status_code=status_code,
        )
        return response.json(payload, status=status_code)

    @app.exception(RequestCancelled)  # type: ignore[arg-type]
    def cancelled_request_handler(_: AppRequest, __: RequestCancelled) -> HTTPResponse:
        logger.warning("Cancel request")
        return response.empty()

    @app.exception(InvalidUpgrade)
    def invalid_upgrade_handler(_: AppRequest, __: InvalidUpgrade) -> HTTPResponse:
        logger.info("Invalid upgrade")
        return response.empty()

    @app.exception(Exception)
    def exception_handler(_: AppRequest, exception: Exception) -> HTTPResponse:
        logger.fatal(
            "Internal error",
            exc_info=(type(exception), exception, exception.__traceback__),
        )
        return response.json(internal_server_error_dict, status=500)
