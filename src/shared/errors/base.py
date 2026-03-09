import abc

from typing import Any, Optional, cast

from shared.serialization import json

_EXCEPTION_REGISTRY: dict[int, type["ApplicationError"]] = {}


class ApplicationErrorMeta(abc.ABCMeta):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
    ) -> type["ApplicationError"]:
        cls = cast(
            "type[ApplicationError]",
            super().__new__(mcls, name, bases, attrs),
        )

        code = getattr(cls, "code", None)
        if code is not None:
            if not isinstance(code, int):
                raise TypeError(f"{name}.code must be int, got {type(code)!r}")

            if code in _EXCEPTION_REGISTRY and _EXCEPTION_REGISTRY[code] is not cls:
                other = _EXCEPTION_REGISTRY[code]
                raise RuntimeError(
                    f"Exception code must be unique. {code} is duplicated: "
                    f"{other.__module__}.{other.__name__} vs {cls.__module__}.{cls.__name__}",
                )
            _EXCEPTION_REGISTRY[code] = cls

        return cls


class ApplicationError(Exception, metaclass=ApplicationErrorMeta):
    message: str
    code: int

    def __init__(
        self,
        *,
        message: str | None = None,
        code: int | None = None,
    ) -> None:
        self.message = message if message is not None else self.message
        self.code = code if code is not None else self.code
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"({self.code}) {self.message}"

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "message": self.message,
            "code": self.code,
            "error": type(self).__name__,
        }

        for name in self._iter_public_payload_fields():
            if hasattr(self, name):
                data[name] = json.to_serializable(getattr(self, name))

        return data

    @classmethod
    def deserialize_error(cls, data: dict[str, Any]) -> Optional["ApplicationError"]:
        code = data.get("code")
        if not isinstance(code, int):
            return None

        exc_cls = _EXCEPTION_REGISTRY.get(code)
        if exc_cls is None:
            return None

        if not issubclass(exc_cls, ApplicationError):
            return None

        args = {**data}

        args.pop("error", None)

        return exc_cls(**args)

    @classmethod
    def _iter_public_payload_fields(cls) -> list[str]:
        merged: dict[str, Any] = {}
        for base in reversed(cls.mro()):
            anns = getattr(base, "__annotations__", None)
            if anns:
                merged.update(anns)

        merged.pop("message", None)
        merged.pop("code", None)

        return list(merged.keys())


class ValidationError(ApplicationError):
    pass


class AuthenticationError(ApplicationError):
    pass


class AuthorizationError(ApplicationError):
    pass


class NotFoundError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass


class RateLimitError(ApplicationError):
    pass


class ExternalServiceError(ApplicationError):
    pass


class InternalError(ApplicationError):
    pass


BadDataError = ValidationError
