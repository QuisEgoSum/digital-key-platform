import copy
import json

from collections.abc import Callable
from contextlib import suppress
from enum import Enum, IntEnum, StrEnum
from typing import Any, Union, cast

import jsonref

from pydantic import BaseModel, TypeAdapter
from sanic import Blueprint, Sanic
from sanic_routing import Route

from infra.openapi.spec import (
    OpenapiRoute,
    OpenapiRouteContent,
    OpenapiRouteParameter,
    OpenapiRouteParameterEnum,
)
from shared.errors.base import ApplicationError

openapi: dict[str, Any] = {
    "paths": {},
    "info": {"title": "", "version": ""},
    "openapi": "3.0.3",
    "tags": [],
    "servers": [],
}
handlers: dict[Callable[..., Any], OpenapiRoute] = {}
override_handlers: dict[str, Callable[..., Any]] = {}
webhook_handlers: dict[str, Callable[..., Any]] = {}

type_to_type: dict[str, Callable[[], dict[str, Any]]] = {
    "str": lambda: {"type": "string"},
    "int": lambda: {"type": "integer"},
    "float": lambda: {"type": "number"},
    "bool": lambda: {"type": "boolean"},
    "dict": lambda: {"type": "dictionary"},
    "list": lambda: {"type": "array", "items": {}},
    "enum": lambda: {"type": "string", "enum": []},
}


def get_raw_openapi() -> dict[str, Any]:
    return openapi


def get_openapi_from_handler(route_handler: Callable[..., Any]) -> OpenapiRoute:
    spec: OpenapiRoute = OpenapiRoute()
    while True:
        if route_handler in handlers:
            spec.merge(handlers[route_handler])
        if hasattr(route_handler, "__wrapped__"):
            route_handler = route_handler.__wrapped__
        else:
            return spec


def extract_methods_url(_: Blueprint, route: Route) -> tuple[str, list[str]]:
    url = ""
    for part in route.parts:
        if part == "":
            continue
        if part.startswith("<"):
            url += "/{" + part.split(":")[0].replace(">", "").replace("<", "") + "}"
        else:
            url += "/" + part
    methods = [*route.methods]
    return url, methods


def extract_route_handler(route: Route, method: str, url: str) -> Callable[..., Any]:
    handler: Callable[..., Any] = route.handler
    if hasattr(handler, "view_class"):
        view_class = handler.view_class
        if hasattr(view_class, method):
            handler = getattr(view_class, method)
    override_handler: Callable[..., Any] | None = override_handlers.get(method + url)
    route_handlers: list[Callable[..., Any]] = list(
        filter(
            lambda h: h is not None,  # type: ignore[arg-type]
            [override_handler, handler],
        ),
    )
    return route_handlers[0]


def assign_doc(doc: str, openapi_route: OpenapiRoute) -> None:
    parts = doc.split("\n")
    openapi_route.summary = ""
    for i, part in enumerate(parts):
        if part != "":
            openapi_route.summary = part
            if i != len(parts) - 1:
                openapi_route.description = "\n".join(
                    (s.strip() for s in parts[i + 1 : :]),
                )
            break


def _is_add_to_openapi(
    route: OpenapiRoute,
    *,
    empty_scopes: bool,
    all_scopes: bool,
    include_scopes: set[str | StrEnum] | None,
) -> bool:
    if route.exclude:
        return False
    if all_scopes:
        return True
    if empty_scopes and not route.scopes:
        return True
    if include_scopes is not None and route.scopes & include_scopes:  # noqa: SIM103
        return True
    return False


def collect(
    app: Sanic[Any, Any],
    *,
    empty_scopes: bool = True,
    all_scopes: bool = True,
    include_scopes: list[str | StrEnum] | None = None,
) -> None:
    include_scopes_set = set(include_scopes) if include_scopes else None
    tags: set[str] = set()
    for bg_name in app.blueprints:
        bg = app.blueprints[bg_name]
        for route in bg.routes:
            webhook_name, methods = extract_methods_url(bg, route)
            for method in methods:
                method = method.lower()
                if method == "options":
                    continue
                handler = extract_route_handler(route, method, webhook_name)
                openapi_route = get_openapi_from_handler(handler) or OpenapiRoute()
                if not _is_add_to_openapi(
                    openapi_route,
                    empty_scopes=empty_scopes,
                    all_scopes=all_scopes,
                    include_scopes=include_scopes_set,
                ):
                    continue
                openapi_route.resolve_tags(webhook_name, bg_name)
                tags = tags.union(openapi_route.tags)
                assign_doc(handler.__doc__ or "", openapi_route)
                if len(openapi_route.responses) == 0:
                    openapi_route.add_response_content(
                        200,
                        OpenapiRouteContent(description="Ok"),
                    )
                if webhook_name not in openapi["paths"]:
                    openapi["paths"][webhook_name] = {method: openapi_route.to_dict()}
                else:
                    openapi["paths"][webhook_name][method] = openapi_route.to_dict()

    openapi["x-webhooks"] = {}

    for method_name, handler in webhook_handlers.items():
        method, webhook_name = method_name.split("#-#")
        webhook_name = method + " " + webhook_name
        method = method.lower()
        openapi_route = get_openapi_from_handler(handler) or OpenapiRoute()
        if not _is_add_to_openapi(
            openapi_route,
            empty_scopes=empty_scopes,
            all_scopes=all_scopes,
            include_scopes=include_scopes_set,
        ):
            continue
        tags = tags.union(openapi_route.tags)
        openapi_route.summary = webhook_name
        openapi_route.description = ""
        for line in (handler.__doc__ or "").split("\n"):
            if line.startswith("    "):
                line = line.replace("    ", "")
            openapi_route.description += line + "\n"
        if len(openapi_route.responses) == 0:
            openapi_route.add_response_content(
                200,
                OpenapiRouteContent(description="Ok"),
            )
        if webhook_name not in openapi["x-webhooks"]:
            openapi["x-webhooks"][webhook_name] = {method: openapi_route.to_dict()}
        else:
            openapi["x-webhooks"][webhook_name][method] = openapi_route.to_dict()

    if not openapi["tags"]:
        openapi["tags"] = [{"name": name} for name in tags]


def upsert(func: Callable[..., Any]) -> OpenapiRoute:
    if func not in handlers:
        handlers[func] = OpenapiRoute()
    return handlers[func]


def object_schema_to_parameters(
    schema: dict[str, Any],
    location: OpenapiRouteParameterEnum = OpenapiRouteParameterEnum.query,
) -> list[OpenapiRouteParameter]:
    parameters = []
    required = set(schema.get("required", []))

    for prop in schema["properties"].items():
        name = prop[0]
        item = prop[1]
        parameters.append(OpenapiRouteParameter(location, name, name in required, item))
    return parameters


def exception_schema_to_response(
    exception: type[ApplicationError],
) -> dict[str, Any]:
    message: dict[str, Any] = {"type": "string"}
    if hasattr(exception, "message"):
        message["default"] = exception.message
    schema: dict[str, Any] = {
        "title": exception.__name__,
        "type": "object",
        "properties": {
            "code": {"type": "integer", "default": exception.code},
            "error": {"type": "string", "default": exception.__name__},
            "message": message,
        },
        "required": ["message", "code", "error"],
    }
    annotations = exception.__dict__.get("__annotations__")
    if annotations:
        for field, annotation in annotations.items():
            is_required = True
            if hasattr(annotation, "__origin__"):
                if annotation.__origin__ is Union:
                    field_type = annotation.__args__[0].__name__
                    is_required = False
                else:
                    field_type = annotation.__origin__.__name__
            elif isinstance(annotation, type) and issubclass(annotation, Enum):
                field_type = "enum"
            else:
                try:
                    field_type = annotation.__name__
                except AttributeError:
                    field_type = "Unknown"
            schema["properties"][field] = type_to_type.get(
                field_type,
                lambda: {
                    "type": "object",
                    "description": "Warning: Couldn't generate type automatically",
                },
            )()
            if hasattr(exception, field):
                schema["properties"][field]["default"] = getattr(exception, field)
            if field_type == "list":
                with suppress(Exception):
                    if issubclass(
                        annotation.__args__[0],
                        ApplicationError,
                    ):
                        schema["properties"][field]["items"] = (
                            exception_schema_to_response(annotation.__args__[0])
                        )
            if field_type == "enum":
                schema["properties"][field]["enum"] = [
                    member.value for member in annotation
                ]
            if is_required:
                schema["required"].append(field)
    return schema


def path_schema_from_raw_parameters(
    name: str,
    path_type: str,
    description: str | None = None,
    enum_cls: Enum | StrEnum | IntEnum | list[str] | None = None,
) -> OpenapiRouteParameter:
    schema: dict[str, Any] = {"type": path_type}
    if enum_cls is not None:
        if not isinstance(enum_cls, list):
            enum_cls = [c.value for c in enum_cls]  # type: ignore
        schema["enum"] = enum_cls
    return OpenapiRouteParameter(
        OpenapiRouteParameterEnum.path,
        name,
        True,
        schema,
        description,
    )


def schema_mapper_factory(
    schema: TypeAdapter[Any] | type[BaseModel] | dict[str, Any],
) -> dict[str, Any]:
    if isinstance(schema, TypeAdapter):
        return copy.deepcopy(
            jsonref.loads(json.dumps(schema.json_schema()), jsonschema=True),
        )
    elif issubclass(schema, BaseModel):  # type: ignore[arg-type]
        schema = cast("type[BaseModel]", schema)
        return copy.deepcopy(
            jsonref.loads(json.dumps(schema.model_json_schema()), jsonschema=True),
        )
    elif isinstance(schema, dict):
        return schema
    else:
        return jsonref.loads(
            json.dumps(TypeAdapter(schema).json_schema()),
            jsonschema=True,
        )
