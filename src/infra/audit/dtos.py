import uuid

from dataclasses import dataclass
from typing import Any

from infra.audit.enums import (
    AuditActionType,
    AuditActorType,
    AuditEventEntityRoleType,
    AuditSubjectType,
)


@dataclass()
class AuditEventDataChangesDTO:
    after: Any
    before: Any | None = None
    reason: str | None = None
    context: dict[str, Any] | None = None


@dataclass()
class AuditEventDataEventEntityDTO:
    type: AuditSubjectType

    id: str | int | uuid.UUID | None = None
    extra: dict[str, Any] | None = None

    role: AuditEventEntityRoleType | None = None


@dataclass()
class AuditEventDataEventType:
    details: Any
    entities: list[AuditEventDataEventEntityDTO] | None = None
    context: dict[str, Any] | None = None


@dataclass()
class AuditEventInputDTO:
    actor_type: AuditActorType

    subject_type: AuditSubjectType

    action: AuditActionType

    actor_key: str | None = None

    subject_id: str | None = None
    subject_extra: dict[str, Any] | None = None

    is_critical: bool = False

    data: AuditEventDataChangesDTO | AuditEventDataEventType | None = None

    correlation_id: str | None = None
