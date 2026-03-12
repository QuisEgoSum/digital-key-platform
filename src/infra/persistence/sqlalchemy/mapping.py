from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from types import UnionType
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
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import RowMapping
from sqlalchemy.engine import Result

from infra.persistence.sqlalchemy.errors import DTOMappingError

T = TypeVar("T")


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
        elif (
            origin in (list, tuple)
            and isinstance(value, Sequence)
            and not isinstance(value, (str, bytes, bytearray))
        ):
            item_type = _unwrap_type(get_args(nested_type)[0])

            items = []
            for inx, item in enumerate(value):
                if is_dataclass(item_type) and isinstance(item, Mapping):
                    items.append(_map_dataclass(cast("Any", item_type), item))
                else:
                    try:
                        items.append(_coerce_scalar(item, item_type))
                    except Exception as ex:
                        raise DTOMappingError(
                            f"Failed to map field '{field_name}[{inx}]' to {item_type}: got value '{item}'",
                        ) from ex

            value = tuple(items) if origin is tuple else items
        else:
            try:
                value = _coerce_scalar(value, nested_type)
            except Exception as ex:
                raise DTOMappingError(
                    f"Failed to map field '{field_name}' to {field_type}: got value '{data[field_name]}'",
                ) from ex

        init_kwargs[field_name] = value

    return dto_cls(**init_kwargs)


def _unwrap_type(tp: Any) -> Any:
    origin = get_origin(tp)
    if origin is Annotated:
        return _unwrap_type(get_args(tp)[0])
    if origin in (Union, UnionType):
        non_none = [arg for arg in get_args(tp) if arg is not type(None)]
        if len(non_none) == 1:
            return _unwrap_type(non_none[0])
    return tp


def _coerce_scalar(value: Any, target_type: Any) -> Any:
    if value is None:
        return None

    if target_type is date:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return date.fromisoformat(value)
        return value

    if isinstance(value, target_type):
        return value

    if target_type is datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

    if target_type is time:
        if isinstance(value, str):
            return time.fromisoformat(value)
        return value

    if target_type is UUID:
        if isinstance(value, str):
            return UUID(value)
        return value

    if target_type is Decimal:
        if isinstance(value, int | float | str):
            return Decimal(str(value))
        return value

    if isinstance(target_type, type) and issubclass(target_type, Enum):
        if isinstance(value, target_type):
            return value
        return target_type(value)

    return value
