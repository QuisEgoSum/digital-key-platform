"""1.0.0-audit

Revision ID: 85408e4c3cfd
Revises:
Create Date: 2026-03-10 16:35:06.984754

"""

import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "85408e4c3cfd"
down_revision = None
branch_labels = None
depends_on = None

audit_actor_type = postgresql.ENUM(
    "admin",
    "user",
    "anonymous",
    "system",
    "external_service",
    name="audit_actor_type",
    schema="infra",
    create_type=False,
)
audit_subject_type = postgresql.ENUM(
    "user",
    "user_action_token",
    "user_session",
    "user_email",
    name="audit_subject_type",
    schema="infra",
    create_type=False,
)
audit_action_type = postgresql.ENUM(
    "login",
    "logout",
    "register",
    "email_verification_request",
    "email_verification_confirm",
    "password_reset_request",
    "password_reset_confirm",
    name="audit_action_type",
    schema="infra",
    create_type=False,
)
audit_result_type = postgresql.ENUM(
    "success",
    "failure",
    "rejected",
    name="audit_result_type",
    schema="infra",
    create_type=False,
)
audit_scope_type = postgresql.ENUM(
    "user",
    "admin",
    name="audit_scope_type",
    schema="infra",
    create_type=False,
)


def upgrade() -> None:
    op.execute("create schema if not exists infra;")

    audit_actor_type.create(op.get_bind())
    audit_subject_type.create(op.get_bind())
    audit_action_type.create(op.get_bind())
    audit_result_type.create(op.get_bind())
    audit_scope_type.create(op.get_bind())

    op.create_table(
        "audit_events",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("actor_type", audit_actor_type, nullable=False),
        sa.Column("subject_type", audit_subject_type, nullable=True),
        sa.Column("scope_type", audit_scope_type, nullable=True),
        sa.Column("action", audit_action_type, nullable=False),
        sa.Column("result", audit_result_type, nullable=True),
        sa.Column(
            "is_critical",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("actor_key", sa.String(), nullable=True),
        sa.Column("subject_id", sa.String(), nullable=True),
        sa.Column("scope_id", sa.String(), nullable=True),
        sa.Column("correlation_id", sa.String(), nullable=True),
        sa.Column(
            "subject_extra",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="infra",
    )

    op.create_index(
        "inx_iae_action_created_at_desc",
        "audit_events",
        ["action", sa.literal_column("created_at DESC")],
        unique=False,
        schema="infra",
    )
    op.create_index(
        "inx_iae_actor_type_actor_key_created_at_desc",
        "audit_events",
        ["actor_type", "actor_key", sa.literal_column("created_at DESC")],
        unique=False,
        schema="infra",
    )
    op.create_index(
        "inx_iae_correlation_id",
        "audit_events",
        ["correlation_id"],
        unique=False,
        schema="infra",
    )
    op.create_index(
        "inx_iae_created_at_desc",
        "audit_events",
        [sa.literal_column("created_at DESC")],
        unique=False,
        schema="infra",
    )
    op.create_index(
        "inx_iae_subject_type_subject_id_created_at_desc",
        "audit_events",
        ["subject_type", "subject_id", sa.literal_column("created_at DESC")],
        unique=False,
        schema="infra",
    )
    op.create_index(
        "inx_iae_scope_type_scope_id_created_at_desc",
        "audit_events",
        ["scope_type", "scope_id", sa.literal_column("created_at DESC")],
        unique=False,
        schema="infra",
    )


def downgrade() -> None:
    op.drop_index(
        "inx_iae_scope_type_scope_id_created_at_desc",
        table_name="audit_events",
        schema="infra",
    )
    op.drop_index(
        "inx_iae_subject_type_subject_id_created_at_desc",
        table_name="audit_events",
        schema="infra",
    )
    op.drop_index("inx_iae_created_at_desc", table_name="audit_events", schema="infra")
    op.drop_index("inx_iae_correlation_id", table_name="audit_events", schema="infra")
    op.drop_index(
        "inx_iae_actor_type_actor_key_created_at_desc",
        table_name="audit_events",
        schema="infra",
    )
    op.drop_index(
        "inx_iae_action_created_at_desc",
        table_name="audit_events",
        schema="infra",
    )
    op.drop_table("audit_events", schema="infra")

    audit_actor_type.drop(op.get_bind())
    audit_subject_type.drop(op.get_bind())
    audit_action_type.drop(op.get_bind())
    audit_result_type.drop(op.get_bind())
    audit_scope_type.drop(op.get_bind())

    op.execute("drop schema if exists infra cascade;")
