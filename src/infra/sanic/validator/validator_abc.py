from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from inspect import isawaitable
from typing import Any, ParamSpec, TypeVar, cast

from infra import openapi
from infra.sanic.http.request import AppRequest
from infra.sanic.validator.enums import TargetNameType
from infra.sanic.validator.errors import NotRequestProvidedError, SchemaValidationError
from infra.sanic.validator.types import RawPayload, SchemaType

P = ParamSpec("P")
R = TypeVar("R")
TP = TypeVar("TP")
TR = TypeVar("TR")


def format_error_message(message: str, field: str) -> str:
    return message.format(field_name=field)


class ValidatorABC[TP, TR](ABC):
    schema: Any
    target_name: TargetNameType

    def __init__(
        self,
        schema: SchemaType,
        target_name: TargetNameType = TargetNameType.BODY,
        pass_data: bool = True,
        docs: bool = True,
    ) -> None:
        self.schema = schema
        self.target_name = target_name
        self.schema_fields = self.get_schema_fields()
        self.schema_query_list_fields = self.get_query_list_fields()
        self.pass_data = pass_data
        self.docs = docs

    def get_target(
        self,
        request: AppRequest,
        kwargs: Any,
    ) -> RawPayload:
        if self.target_name == TargetNameType.BODY:
            if request.json is None:
                raise NotRequestProvidedError(self.target_name)
            return request.json
        elif self.target_name == TargetNameType.QUERY:
            query: dict[str, Any] = {}
            for key, value in request.args.items():
                if key in self.schema_query_list_fields:
                    query[key] = value
                else:
                    query[key] = value[0]
            return query
        elif self.target_name == TargetNameType.PARAMS:
            params = {}
            for name in self.schema_fields:
                if name in kwargs:
                    params[name] = kwargs.pop(name)
                else:
                    raise NotRequestProvidedError(self.target_name)
            return params
        elif self.target_name == TargetNameType.HEADERS:
            return {k.lower(): v for k, v in request.headers.items()}
        return None

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        @openapi.errors(SchemaValidationError, NotRequestProvidedError)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            request = cast("AppRequest", args[0])
            target = cast("TP", self.get_target(request, kwargs))
            validated = self.validate(target)
            if self.pass_data:
                kwargs[self.target_name.value] = validated
            result = func(*args, **kwargs)
            if isawaitable(result):
                return await result
            return result

        if self.docs:
            getattr(openapi, self.target_name.value)(self.schema)(func)

        return cast("Callable[P, R]", wrapper)

    @abstractmethod
    def get_query_list_fields(self) -> set[str]:
        """
        Return a set of schema field names that expect multiple values
        for the QUERY validator (i.e., list-typed query parameters).
        """

        ...

    @abstractmethod
    def validate(self, payload: TP) -> TR: ...

    @abstractmethod
    def get_schema_fields(self) -> list[str]:
        """
        Return a list of schema field names used by the PARAMS validator.
        """

        ...
