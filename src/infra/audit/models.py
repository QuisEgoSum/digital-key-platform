from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Index, String, false
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from infra.audit.enums import (
    AuditActionType,
    AuditActorType,
    AuditSubjectType,
)
from infra.persistence.postgresql.columns import created_at_column
from infra.persistence.postgresql.models import BaseBigIntegerPK


class AuditEventRow(BaseBigIntegerPK):
    __tablename__ = "audit_events"
    __table_args__ = ({"schema": "infra"},)

    # ------------------------------------------------------------------------------------------------------------------
    # Event source
    # ------------------------------------------------------------------------------------------------------------------
    actor_type: Mapped[AuditActorType] = mapped_column(
        ENUM(AuditActorType, name="audit_actor_type", schema="infra"),
        nullable=False,
    )
    actor_key: Mapped[str | None] = mapped_column(String(), nullable=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Event subject
    # ------------------------------------------------------------------------------------------------------------------

    subject_type: Mapped[AuditSubjectType] = mapped_column(
        ENUM(AuditSubjectType, name="audit_subject_type", schema="infra"),
        nullable=False,
    )
    subject_id: Mapped[str] = mapped_column(String(), nullable=True)
    subject_extra: Mapped[dict[str, Any]] = mapped_column(JSONB(), nullable=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Event type
    # ------------------------------------------------------------------------------------------------------------------

    action: Mapped[AuditActionType] = mapped_column(
        ENUM(AuditActionType, name="audit_action_type", schema="infra"),
        nullable=False,
    )
    is_critical: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        server_default=false(),
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Details
    # ------------------------------------------------------------------------------------------------------------------

    # Event payload.
    data: Mapped[dict[str, Any]] = mapped_column(JSONB(), nullable=True)
    # trace_id/span_id.
    correlation_id: Mapped[str] = mapped_column(String(), nullable=True)

    created_at: Mapped[datetime] = created_at_column()

    inx_iae_created_at_desc = Index(
        "inx_iae_created_at_desc",
        created_at.desc(),
    )
    inx_iae_subject_type_subject_id_created_at_desc = Index(
        "inx_iae_subject_type_subject_id_created_at_desc",
        subject_type,
        subject_id,
        created_at.desc(),
    )
    inx_iae_actor_type_actor_key_created_at_desc = Index(
        "inx_iae_actor_type_actor_key_created_at_desc",
        actor_type,
        actor_key,
        created_at.desc(),
    )
    inx_iae_action_created_at_desc = Index(
        "inx_iae_action_created_at_desc",
        created_at.desc(),
    )
    inx_iae_correlation_id = Index(
        "inx_iae_correlation_id",
        correlation_id,
    )
