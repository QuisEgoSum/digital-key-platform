import uuid

from typing import Any

from infra.audit.enums import (
    AuditActionType,
    AuditActorType,
    AuditEntityType,
    AuditResultType,
    AuditScopeType,
    AuditSubjectType,
)
from infra.audit.models import AuditEventRow


def audit_event_asserts(
    audit_event: AuditEventRow,
    *,
    actor_type: AuditActorType,
    actor_key: str | int | uuid.UUID | None = None,
    subject_type: AuditSubjectType | None = None,
    subject_id: str | int | uuid.UUID | None = None,
    subject_extra: dict[str, Any] | None = None,
    scope_type: AuditScopeType | None = None,
    scope_id: str | int | None = None,
    result: AuditResultType | None = None,
    action: AuditActionType,
    ip_address: str | None = None,
    outcome: str | None = None,
    details: dict[str, Any] | None = None,
    entities: list[dict[str, Any]] | None = None,
    entity_types: list[AuditEntityType] | None = None,
) -> None:
    if actor_key is not None:
        actor_key = str(actor_key)
    if subject_id is not None:
        subject_id = str(subject_id)
    if scope_id is not None:
        scope_id = str(scope_id)

    assert audit_event.actor_type == actor_type, (
        f"audit_event.actor_type mismatch: "
        f"expected={actor_type!r}, actual={audit_event.actor_type!r}"
    )
    assert audit_event.actor_key == actor_key, (
        f"audit_event.actor_key mismatch: "
        f"expected={actor_key!r}, actual={audit_event.actor_key!r}"
    )
    assert audit_event.subject_type == subject_type, (
        f"audit_event.subject_type mismatch: "
        f"expected={subject_type!r}, actual={audit_event.subject_type!r}"
    )
    assert audit_event.subject_id == subject_id, (
        f"audit_event.subject_id mismatch: "
        f"expected={subject_id!r}, actual={audit_event.subject_id!r}"
    )
    assert audit_event.subject_extra == subject_extra, (
        f"audit_event.subject_extra mismatch: "
        f"expected={subject_extra!r}, actual={audit_event.subject_extra!r}"
    )
    assert audit_event.scope_type == scope_type, (
        f"audit_event.scope_type mismatch: "
        f"expected={scope_type!r}, actual={audit_event.scope_type!r}"
    )
    assert audit_event.scope_id == scope_id, (
        f"audit_event.scope_id mismatch: "
        f"expected={scope_id!r}, actual={audit_event.scope_id!r}"
    )
    assert audit_event.result == result, (
        f"audit_event.result mismatch: "
        f"expected={result!r}, actual={audit_event.result!r}"
    )
    assert audit_event.action == action, (
        f"audit_event.action mismatch: "
        f"expected={action!r}, actual={audit_event.action!r}"
    )
    assert audit_event.ip_address == ip_address, (
        f"audit_event.ip_address mismatch: "
        f"expected={ip_address!r}, actual={audit_event.ip_address!r}"
    )

    if outcome is not None:
        actual_outcome = None
        if audit_event.data is not None:
            actual_outcome = audit_event.data.get("details", {}).get("outcome")

        assert actual_outcome == outcome, (
            f"audit_event.data.details.outcome mismatch: "
            f"expected={outcome!r}, actual={actual_outcome!r}, "
            f"data={audit_event.data!r}"
        )

    if details is not None:
        assert audit_event.data.get("details") == details, (
            f"audit_event.data.details mismatch: "
            f"expected={details!r}, actual={audit_event.data.get('details')!r}"
        )

    if entities is not None:
        actual_entities = audit_event.data.get("entities") if audit_event.data else None
        assert actual_entities == entities, (
            f"audit_event.data.entities mismatch: "
            f"expected={entities!r}, \nactual={actual_entities!r}"
        )

    if entity_types is not None:
        actual_entities = audit_event.data.get("entities") if audit_event.data else None
        assert actual_entities is not None, (
            "audit_event.data.entities is missing, "
            f"expected entity types={entity_types!r}, data={audit_event.data!r}"
        )

        actual_entity_types = {entity["type"] for entity in actual_entities}
        missing_entity_types = [
            expected for expected in entity_types if expected not in actual_entity_types
        ]

        assert not missing_entity_types, (
            f"audit_event.data.entities types mismatch: "
            f"missing={missing_entity_types!r}, "
            f"actual_types={sorted(actual_entity_types)!r}, "
            f"entities={actual_entities!r}"
        )
