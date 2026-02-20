from shared.errors.base import (
    ApplicationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ExternalServiceError,
    InternalError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

DEFAULT_HTTP_STATUS_BY_BASE: list[tuple[type[ApplicationError], int]] = [
    (ValidationError, 400),
    (AuthenticationError, 401),
    (AuthorizationError, 403),
    (NotFoundError, 404),
    (ConflictError, 409),
    (RateLimitError, 429),
    (ExternalServiceError, 502),
    (InternalError, 500),
]

_HTTP_STATUS_OVERRIDES: dict[type[ApplicationError], int] = {}


def get_http_status(exc: type[ApplicationError] | ApplicationError) -> int:
    exc_cls = type(exc) if isinstance(exc, ApplicationError) else exc

    status = _HTTP_STATUS_OVERRIDES.get(exc_cls)
    if status is not None:
        return status

    for base_cls, base_status in DEFAULT_HTTP_STATUS_BY_BASE:
        if issubclass(exc_cls, base_cls):
            return base_status

    return 500
