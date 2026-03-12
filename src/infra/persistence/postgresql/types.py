from enum import Enum
from typing import Any

from sqlalchemy.dialects.postgresql import ENUM


def sa_enum(enum: type[Enum], name: str, **kwargs: Any) -> ENUM:
    return ENUM(
        enum,
        name=name,
        values_callable=lambda x: [e.value for e in x],
        **kwargs,
    )
