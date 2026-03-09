import json
import uuid

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any

import orjson

from pydantic import BaseModel
from sqlalchemy import Row, RowMapping

from shared.errors import base
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

    if isinstance(obj, Enum):
        return obj.value, True

    if isinstance(obj, base.ApplicationError):
        return obj.to_dict(), True

    if is_namedtuple_instance(obj):
        # noinspection PyProtectedMember
        return obj._asdict(), True

    return obj, False


def strict_serializer(obj: Any) -> Any:
    converted, handled = _convert_common(obj)
    if handled:
        return converted
    raise TypeError(f"Type {type(obj)} not serializable")


def soft_serializer(obj: Any) -> Any:
    converted, handled = _convert_common(obj)
    if handled:
        return converted
    return repr(obj)


def origin_serializer(obj: Any) -> Any:
    converted, handled = _convert_common(obj)
    if handled:
        return converted
    return obj


def strict_json_dumps(o: Any, **kwargs: Any) -> str:
    kwargs["default"] = strict_serializer
    return json.dumps(o, **kwargs)


def soft_json_dumps(o: Any, **kwargs: Any) -> str:
    kwargs["default"] = soft_serializer
    return json.dumps(o, **kwargs)


def strict_orjson_dumps(o: Any, **kwargs: Any) -> bytes:
    kwargs["default"] = strict_serializer
    return orjson.dumps(o, **kwargs)


def soft_orjson_dumps(o: Any, **kwargs: Any) -> bytes:
    kwargs["default"] = soft_serializer
    return orjson.dumps(o, **kwargs)


def to_serializable(obj: object) -> Any:
    obj = origin_serializer(obj)
    if isinstance(obj, Mapping):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_serializable(v) for v in obj]
    return obj
