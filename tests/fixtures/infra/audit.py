from collections.abc import Sequence
from dataclasses import dataclass

import pytest

from sqlalchemy import select

from infra.audit.models import AuditEventRow
from infra.persistence.postgresql.connection import DBContext


@dataclass()
class GetAuditEventsFactory:
    db: DBContext

    async def __call__(self) -> Sequence[AuditEventRow]:
        async with self.db.session():
            stmt = select(AuditEventRow).order_by(AuditEventRow.id.asc())
            result = await self.db.execute(stmt)
            return result.scalars().all()


@pytest.fixture()
def get_audit_events_factory(db_context: DBContext) -> GetAuditEventsFactory:
    return GetAuditEventsFactory(db_context)
