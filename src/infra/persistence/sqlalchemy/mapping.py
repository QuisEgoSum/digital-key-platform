from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from typing import (
    Annotated,
    Any,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import BaseModel
from sqlalchemy import RowMapping
from sqlalchemy.engine import Result

T = TypeVar("T")


def _map_dataclass[T](dto_cls: type[T], data: Mapping[str, Any] | RowMapping) -> T:
    if not is_dataclass(dto_cls):
        raise TypeError(f"{dto_cls} is not a dataclass")

    type_hints = get_type_hints(dto_cls)
    init_kwargs: dict[str, Any] = {}

    for field in fields(dto_cls):
        field_name = field.name
        field_type = type_hints.get(field_name)

        if field_name not in data:
            continue

        value = data[field_name]

        nested_type = _unwrap_type(field_type)
        origin = get_origin(nested_type)

        if is_dataclass(nested_type) and isinstance(value, Mapping):
            value = _map_dataclass(cast("Any", nested_type), value)
        elif origin in (list, tuple) and isinstance(value, Sequence):
            item_type = _unwrap_type(get_args(nested_type)[0])
            if is_dataclass(item_type):
                value = [
                    (
                        _map_dataclass(cast("Any", item_type), v)
                        if isinstance(v, Mapping)
                        else v
                    )
                    for v in value
                ]
                if origin is tuple:
                    value = tuple(value)

        init_kwargs[field_name] = value

    return dto_cls(**init_kwargs)


def _unwrap_type(tp: Any) -> Any:
    origin = get_origin(tp)
    if origin is Annotated:
        return _unwrap_type(get_args(tp)[0])
    if origin is Union:
        non_none = [arg for arg in get_args(tp) if arg is not type(None)]
        if len(non_none) == 1:
            return _unwrap_type(non_none[0])
    return tp


def mapping_to_cls[T](mapping: RowMapping, dto_cls: type[T]) -> T:
    if issubclass(dto_cls, BaseModel):
        return dto_cls.model_validate(mapping)
    return _map_dataclass(dto_cls, mapping)


def mapping_first_result_to_dto[T](
    result: Result[tuple[Any, ...]],
    dto_cls: type[T],
) -> T | None:
    mapping = result.mappings().first()
    return mapping_to_cls(mapping, dto_cls) if mapping else None


def mapping_one_result_to_dto[T](
    result: Result[tuple[Any, ...]],
    dto_cls: type[T],
) -> T:
    mapping = result.mappings().one()
    return mapping_to_cls(mapping, dto_cls)


def mapping_all_result_to_dto[T](
    result: Result[tuple[Any, ...]],
    dto_cls: type[T],
) -> Sequence[T]:
    return [mapping_to_cls(mapping, dto_cls) for mapping in result.mappings().all()]
