from infra.audit import audit_event_service
from infra.audit.dtos import AuditEventCommand
from infra.persistence.postgresql.connection import db
from shared.utils.decorators import catch_and_log


@catch_and_log()
async def record_events(*events: AuditEventCommand) -> None:
    async with db.new_transaction():
        await audit_event_service.record_events(events)
