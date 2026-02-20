from collections.abc import Sequence
from typing import Any

from sqlalchemy import insert

from infra.audit.models import AuditEventRow
from infra.persistence.postgresql.connection import db


async def insert_audit_events(events: Sequence[dict[str, Any]]) -> None:
    stmt = insert(AuditEventRow).values(events)
    await db.execute(stmt)
