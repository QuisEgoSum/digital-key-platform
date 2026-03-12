from collections.abc import Sequence

from infra.audit import audit_event_service
from infra.audit.dtos import AuditEventCommand
from infra.persistence.postgresql.connection import db
from shared.utils.logger import get_logger

logger = get_logger(__name__)


async def record_events(events: Sequence[AuditEventCommand]) -> None:
    await audit_event_service.record_events(events)


async def record_event(
    event: AuditEventCommand,
) -> None:
    await record_events([event])


async def record_events_in_new_tx(events: Sequence[AuditEventCommand]) -> None:
    async with db.new_transaction():
        await record_events(events)


async def record_event_in_new_tx(event: AuditEventCommand) -> None:
    await record_events_in_new_tx([event])
