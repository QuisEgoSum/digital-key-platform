import copy
import json

from typing import TYPE_CHECKING, Any, Literal, get_args, get_origin

import jsonref

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, create_model

if TYPE_CHECKING:
    from shared.errors.base import ApplicationError


class ErrorOutputDTO(BaseModel):
    message: str
    code: int
    error: str


def _build_payload_model_for_exception(
    exc_cls: type[Any],
    cache: dict[type[Any], type[BaseModel]],
) -> type[BaseModel]:
    if exc_cls in cache:
        return cache[exc_cls]

    ann_map: dict[str, Any] = getattr(exc_cls, "__annotations__", {}) or {}

    fields: dict[str, Any] = {}
    model_name = f"{exc_cls.__name__}Payload"

    for name, ann in ann_map.items():
        normalized_ann = _normalize_annotation(ann, cache)

        default = getattr(exc_cls, name, ...)
        if default is ...:
            fields[name] = (normalized_ann, Field(default=...))
        else:
            fields[name] = (normalized_ann, Field(default=default))

    Payload = create_model(
        model_name,
        __config__=ConfigDict(arbitrary_types_allowed=True),
        **fields,
    )
    cache[exc_cls] = Payload
    return Payload


def _normalize_annotation(ann: Any, cache: dict[type[Any], type[BaseModel]]) -> Any:
    origin = get_origin(ann)
    if origin is None:
        if isinstance(ann, type) and issubclass(ann, Exception):
            return _build_payload_model_for_exception(ann, cache)

        return ann

    args = get_args(ann)

    normalized_args = tuple(_normalize_annotation(a, cache) for a in args)

    try:
        return origin[normalized_args]
    except TypeError:
        return ann


def exception_to_openapi(exc_cls: type["ApplicationError"]) -> dict[str, Any]:
    payload_cache: dict[type[Any], type[BaseModel]] = {}

    fields: dict[str, Any] = {
        "code": (Literal[exc_cls.code], Field(default=exc_cls.code)),
        "error": (Literal[exc_cls.__name__], Field(default=exc_cls.__name__)),
        "message": (str, Field(default=getattr(exc_cls, "message", ""))),
    }

    extra_ann = getattr(exc_cls, "__annotations__", {}) or {}
    for name, ann in extra_ann.items():
        normalized_ann = _normalize_annotation(ann, payload_cache)

        default = getattr(exc_cls, name, ...)
        if default is ...:
            fields[name] = (normalized_ann, Field(default=...))
        else:
            fields[name] = (normalized_ann, Field(default=default))

    model_name = f"{exc_cls.__name__}"
    Variant = create_model(
        model_name,
        __base__=ErrorOutputDTO,
        __config__=ConfigDict(arbitrary_types_allowed=True),
        **fields,
    )
    return copy.deepcopy(
        jsonref.loads(json.dumps(TypeAdapter(Variant).json_schema()), jsonschema=True),
    )
