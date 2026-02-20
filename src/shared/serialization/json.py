import json
import uuid

from collections.abc import Callable, Mapping
from dataclasses import asdict, is_dataclass
from datetime import date
from decimal import Decimal
from enum import Enum, StrEnum
from typing import Any

import orjson

from pydantic import BaseModel
from sqlalchemy import Row, RowMapping

from shared.errors.base import ApplicationError
from shared.utils.typing_utils import is_namedtuple_instance


def _convert_common(obj: Any) -> tuple[Any, bool]:
    if isinstance(obj, date):
        return obj.isoformat(), True

    if isinstance(obj, uuid.UUID):
        return str(obj), True

    if isinstance(obj, RowMapping):
        return dict(obj), True

    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json"), True

    if isinstance(obj, Row):
        # noinspection PyProtectedMember
        return dict(obj._asdict()), True

    if is_dataclass(obj):
        return asdict(obj), True  # type: ignore[arg-type]

    if isinstance(obj, Decimal):
        return str(obj), True

    if isinstance(obj, (Enum, StrEnum)):
        return obj.value, True

    if isinstance(obj, ApplicationError):
        return obj.to_dict(), True

    if is_namedtuple_instance(obj):
        # noinspection PyProtectedMember
        return obj._asdict(), True

    return obj, False


def json_serializer_factory(
    *,
    strict: bool = True,
    origin: bool = False,
) -> Callable[[Any], Any]:
    def json_serializer(obj: Any) -> Any:
        converted, handled = _convert_common(obj)
        if handled:
            return converted

        if strict:
            raise TypeError(f"Type {type(obj)} not serializable")

        if origin:
            return obj

        return repr(obj)

    return json_serializer


def orjson_serializer_factory(*, strict: bool = True) -> Callable[[Any], Any]:
    def orjson_serializer(obj: Any) -> Any:
        converted, handled = _convert_common(obj)
        if handled:
            return converted

        if strict:
            raise TypeError(f"Type {type(obj)} not serializable")

        return repr(obj)

    return orjson_serializer


def strict_json_dumps(o: Any, **kwargs: Any) -> str:
    kwargs["default"] = json_serializer_factory(strict=True)
    return json.dumps(o, **kwargs)


def soft_json_dumps(o: Any, **kwargs: Any) -> str:
    kwargs["default"] = json_serializer_factory(strict=False)
    return json.dumps(o, **kwargs)


def strict_orjson_dumps(o: Any, **kwargs: Any) -> bytes:
    kwargs["default"] = orjson_serializer_factory(strict=True)
    return orjson.dumps(o, **kwargs)


def soft_orjson_dumps(o: Any, **kwargs: Any) -> bytes:
    kwargs["default"] = orjson_serializer_factory(strict=False)
    return orjson.dumps(o, **kwargs)


_soft_origin_serializer = json_serializer_factory(strict=False, origin=True)


def to_serializable(obj: object) -> Any:
    obj = _soft_origin_serializer(obj)
    if isinstance(obj, Mapping):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_serializable(v) for v in obj]
    return obj
