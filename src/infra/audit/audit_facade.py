from collections.abc import Sequence

from infra.audit import audit_event_service
from infra.audit.dtos import AuditEventInputDTO
from shared.utils.logger import get_logger

logger = get_logger(__name__)


async def append_events(
    events: Sequence[AuditEventInputDTO],
    *,
    in_separate_transaction: bool = False,
) -> None:
    if in_separate_transaction:
        try:
            await audit_event_service.append_audit_events(
                events,
                in_separate_transaction=in_separate_transaction,
            )
        except Exception:
            logger.exception("Failed to insert audit events")
    await audit_event_service.append_audit_events(
        events,
        in_separate_transaction=in_separate_transaction,
    )


async def append_event(
    *,
    in_separate_transaction: bool = False,
    event: AuditEventInputDTO,
) -> None:
    await append_events(
        [event],
        in_separate_transaction=in_separate_transaction,
    )
