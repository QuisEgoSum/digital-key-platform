from dataclasses import dataclass

import pytest

from infra.audit.models import AuditEventRow
from infra.persistence.postgresql.connection import DBContext
from utils.query import BaseQuery


@dataclass()
class AuditEventQuery(BaseQuery[AuditEventRow, int]):
    db: DBContext


@pytest.fixture()
def audit_event_query(db_context: DBContext) -> AuditEventQuery:
    return AuditEventQuery(db_context, AuditEventRow, AuditEventRow.id)
