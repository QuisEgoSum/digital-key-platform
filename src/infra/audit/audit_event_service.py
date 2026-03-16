import uuid

from collections.abc import Sequence
from typing import Any

from infra.audit import audit_event_dao
from infra.audit.dtos import AuditEventCommand
from shared.serialization.json import to_serializable
from shared.utils.tracing import get_trace_signature


async def record_events(events: Sequence[AuditEventCommand]) -> None:
    correlation_id = get_trace_signature()

    mapped_events: list[dict[str, Any]] = []

    for event in events:
        mapped_event: dict[str, Any] = {
            "actor_type": event.actor_type,
            "actor_key": _stringify_nullable(event.actor_key),
            "subject_type": event.subject_type,
            "subject_id": _stringify_nullable(event.subject_id),
            "scope_type": event.scope_type,
            "scope_id": _stringify_nullable(event.scope_id),
            "ip_address": event.ip_address,
            "action": event.action,
            "result": event.result,
            "is_critical": event.is_critical,
            "correlation_id": event.correlation_id or correlation_id,
        }
        if event.subject_extra:
            mapped_event["subject_extra"] = to_serializable(event.subject_extra)
        else:
            mapped_event["subject_extra"] = None
        if event.data:
            mapped_event["data"] = to_serializable(event.data)
        else:
            mapped_event["data"] = None

        mapped_events.append(mapped_event)

    return await audit_event_dao.insert_audit_events(mapped_events)


def _stringify_nullable(value: str | int | uuid.UUID | None) -> str | None:
    return str(value) if value is not None else None
