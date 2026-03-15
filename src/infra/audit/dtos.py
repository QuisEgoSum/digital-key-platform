import uuid

from dataclasses import dataclass
from typing import Any

from infra.audit.enums import (
    AuditActionType,
    AuditActorType,
    AuditEntityType,
    AuditEventEntityRoleType,
    AuditResultType,
    AuditScopeType,
    AuditSubjectType,
)


@dataclass()
class AuditChangesDTO:
    after: Any
    before: Any | None = None
    reason: str | None = None
    context: dict[str, Any] | None = None


@dataclass()
class AuditEntityRefDTO:
    type: AuditEntityType
    id: str | int | uuid.UUID | None = None
    extra: dict[str, Any] | None = None
    role: AuditEventEntityRoleType | None = None


@dataclass()
class AuditEventDetailsDTO:
    details: Any = None
    entities: list[AuditEntityRefDTO] | None = None
    context: dict[str, Any] | None = None


@dataclass()
class AuditEventCommand:
    actor_type: AuditActorType
    action: AuditActionType

    scope_type: AuditScopeType | None
    scope_id: int | str | uuid.UUID | None

    ip_address: str | None

    subject_type: AuditSubjectType | None = None

    result: AuditResultType | None = None

    actor_key: str | int | uuid.UUID | None = None

    subject_id: str | int | uuid.UUID | None = None
    subject_extra: dict[str, Any] | None = None

    is_critical: bool = False

    data: AuditChangesDTO | AuditEventDetailsDTO | None = None

    correlation_id: str | None = None
