from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import MappedColumn, mapped_column

from shared.utils.datetime_utils import current_datetime


def created_at_column(comment: str | None = None) -> MappedColumn[datetime]:
    return mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        default=current_datetime,
        comment=comment,
    )


def timestamp_column(nullable: bool = True, **kwargs: Any) -> MappedColumn[datetime]:
    return mapped_column(TIMESTAMP(timezone=True), nullable=nullable, **kwargs)


def updated_at_column() -> MappedColumn[Any]:
    return timestamp_column(
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        default=current_datetime,
        onupdate=current_datetime,
    )
