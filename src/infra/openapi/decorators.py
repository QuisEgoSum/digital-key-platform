from collections.abc import Callable
from decimal import Decimal
from enum import Enum, IntEnum, StrEnum
from typing import Any, ParamSpec, TypeVar

from pydantic import BaseModel, TypeAdapter

from infra.http.adapters.exception_to_http import get_http_status
from infra.openapi.adapters.exception_to_openapi import exception_to_openapi
from infra.openapi.enum import STATUS_TO_DESCRIPTION
from infra.openapi.spec import (
    OpenapiRouteContent,
    OpenapiRouteParameter,
    OpenapiRouteParameterEnum,
)
from infra.openapi.utils import (
    object_schema_to_parameters,
    override_handlers,
    path_schema_from_raw_parameters,
    schema_mapper_factory,
    upsert,
    webhook_handlers,
)
from shared.errors.base import ApplicationError

SchemaType = TypeAdapter[Any] | type[BaseModel] | type[Any]
P = ParamSpec("P")
R = TypeVar("R")


def response_file(
    content_type: str = "*/*",
    status: int = 200,
    description: str | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if description is None:
        description = STATUS_TO_DESCRIPTION.get(status, None)

    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_response_schema(
            status,
            {"description": "File", "type": "string", "format": "binary"},
            content_type,
            description,
        )
        return func

    return inner


def body_form_data_file(
    name: str = "file",
    description: str | None = None,
    required: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    schema = {
        "type": "object",
        "properties": {
            name: {"description": "File", "type": "string", "format": "binary"},
        },
        "required": [name] if required else [],
    }
    if description is not None:
        schema["description"] = description

    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_body_schema("multipart/form-data", schema)
        return func

    return inner


def body_form_data_files(
    name: str = "files",
    required: bool = True,
    max_items: int = 1,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            name: {
                "type": "array",
                "items": {"description": "File", "type": "string", "format": "binary"},
            },
        },
        "required": [name] if required else [],
    }
    if max_items is not None:
        schema["properties"][name]["maxItems"] = max_items

    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_body_schema("multipart/form-data", schema)
        return func

    return inner


def body_binary(
    content_type: str = "*/*",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_body_schema(
            content_type,
            {"description": "File", "type": "string", "format": "binary"},
        )
        return func

    return inner


def tag(
    tag_name: str,
    includes: str | None = None,
    excludes: str | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_tag_fabric(tag_name, includes, excludes)
        return func

    return inner


def exclude() -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).exclude = True
        return func

    return inner


def handler(method: str, url: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        override_handlers[method + url] = func
        return func

    return inner


def webhook(method: str, name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        webhook_handlers[method + "#-#" + name] = func
        return func

    return inner


def scope(scope_name: str | StrEnum) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_scope(scope_name)
        return func

    return inner


def no_content(status: int = 204) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_response_content(
            status,
            OpenapiRouteContent(description="No content"),
        )
        return func

    return inner


def deprecated() -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).deprecated = True
        return func

    return inner


def errors(
    *exceptions: type[ApplicationError],
    content_type: str = "application/json",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        spec = upsert(func)
        for exception in exceptions:
            status_code = get_http_status(exception)
            spec.add_response_schema(
                status=status_code,
                schema=exception_to_openapi(exception),
                content_type=content_type,
                description=STATUS_TO_DESCRIPTION.get(status_code, None),
            )
        return func

    return inner


def header(
    name: str,
    schema_type: str = "string",
    description: str | None = None,
    required: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_parameters(
            [
                OpenapiRouteParameter(
                    location=OpenapiRouteParameterEnum.header,
                    name=name,
                    required=required,
                    schema={"type": schema_type},
                    description=description,
                ),
            ],
        )
        return func

    return inner


def headers(schema: type[BaseModel]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        _headers = []

        for field_name, field in schema.model_fields.items():
            schema_type = "string"
            if field.annotation is int:
                schema_type = "integer"
            if field.annotation in (float, Decimal):
                schema_type = "number"
            _headers.append(
                OpenapiRouteParameter(
                    location=OpenapiRouteParameterEnum.header,
                    name=field.alias or field_name,
                    required=field.is_required(),
                    schema={"type": schema_type},
                    description=field.description,
                ),
            )

        upsert(func).add_parameters(_headers)

        return func

    return inner


def response_header(
    name: str,
    schema_type: str = "string",
    status: int = 200,
    content_type: str = "application/json",
    description: str = "",
    required: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_response_schema(
            status=status,
            schema=None,
            content_type=content_type,
            headers={
                name: {
                    "description": description,
                    "schema": {"type": schema_type},
                    "required": required,
                },
            },
        )
        return func

    return inner


def body(
    schema: SchemaType,
    content_type: str = "application/json",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_body_schema(content_type, schema_mapper_factory(schema))
        return func

    return inner


def body_one_of(
    schemas: list[SchemaType],
    content_type: str = "application/json",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        spec = upsert(func)
        for schema in schemas:
            spec.add_body_schema(content_type, schema_mapper_factory(schema))
        return func

    return inner


def query(schema: SchemaType) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_parameters(
            object_schema_to_parameters(schema_mapper_factory(schema)),
        )
        return func

    return inner


def response(
    schema: SchemaType,
    status: int = 200,
    content_type: str = "application/json",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_response_schema(
            status,
            schema_mapper_factory(schema),
            content_type,
            STATUS_TO_DESCRIPTION.get(status, None),
        )
        return func

    return inner


def responses(
    schemas: list[SchemaType],
    status: int = 200,
    content_type: str = "application/json",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        spec = upsert(func)
        for schema in schemas:
            spec.add_response_schema(
                status,
                schema_mapper_factory(schema),
                content_type,
                STATUS_TO_DESCRIPTION.get(status, None),
            )
        return func

    return inner


def path(
    schema: SchemaType | str,
    path_type: str | None = None,
    description: str = "",
    enum: Enum | StrEnum | IntEnum | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if isinstance(schema, str) and isinstance(path_type, str):
        parameters = [
            path_schema_from_raw_parameters(schema, path_type, description, enum),
        ]
    elif not isinstance(schema, str):
        parameters = object_schema_to_parameters(
            schema_mapper_factory(schema),
            OpenapiRouteParameterEnum.path,
        )
    else:
        parameters = []

    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_parameters(parameters)
        return func

    return inner


params = path


def security(
    name: str,
    scopes: list[str] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def inner(func: Callable[P, R]) -> Callable[P, R]:
        upsert(func).add_security(name, scopes)
        return func

    return inner
