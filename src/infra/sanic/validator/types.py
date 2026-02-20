from typing import Any

from pydantic import BaseModel

RawPayload = dict[str, Any] | list[Any] | None
SchemaType = type[BaseModel]
