"""1.0.0-user

Revision ID: dd30d120ef75
Revises: 85408e4c3cfd
Create Date: 2026-03-10 16:38:50.606608

"""

import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "dd30d120ef75"
down_revision = "85408e4c3cfd"
branch_labels = None
depends_on = None


user_status_type = postgresql.ENUM(
    "active",
    "blocked",
    "banned",
    "deleted",
    name="user_status_type",
    schema="user",
    create_type=False,
)
user_auth_token_kind_type = postgresql.ENUM(
    "email_verification",
    "password_reset",
    name="user_auth_token_kind_type",
    schema="user",
    create_type=False,
)
user_action_token_status_type = postgresql.ENUM(
    "active",
    "canceled",
    "used",
    name="user_action_token_status_type",
    schema="user",
    create_type=False,
)
user_action_token_channel_type = postgresql.ENUM(
    "email",
    name="user_action_token_channel_type",
    schema="user",
    create_type=False,
)


def upgrade() -> None:
    op.execute('create schema if not exists "user";')

    user_status_type.create(op.get_bind())
    user_auth_token_kind_type.create(op.get_bind())
    user_action_token_status_type.create(op.get_bind())
    user_action_token_channel_type.create(op.get_bind())

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("status", user_status_type, nullable=False),
        sa.Column(
            "status_until_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
            comment="User blocked until date.",
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("locale", sa.String(length=16), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="user",
    )

    op.create_index(
        "inx_uu_status_until_at_blocked",
        "users",
        ["status_until_at"],
        unique=False,
        schema="user",
        postgresql_where=sa.text("status = 'blocked'"),
    )

    op.create_table(
        "user_action_tokens",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("expires_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("kind", user_auth_token_kind_type, nullable=False),
        sa.Column(
            "status",
            user_action_token_status_type,
            server_default="active",
            nullable=False,
        ),
        sa.Column("channel", user_action_token_channel_type, nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("short_token_hash", sa.String(), nullable=False),
        sa.Column("long_token_hash", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.users.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="user",
    )

    op.create_index(
        "inx_uuat_user_id_created_at_desc",
        "user_action_tokens",
        ["user_id", sa.literal_column("created_at DESC")],
        unique=False,
        schema="user",
    )
    op.create_index(
        "inx_uuat_user_id_kind_status_active_unq",
        "user_action_tokens",
        ["user_id", "kind"],
        unique=True,
        schema="user",
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index(
        "inx_uuat_long_token_hash_active",
        "user_action_tokens",
        ["long_token_hash"],
        unique=False,
        schema="user",
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "user_credentials",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "password_changed_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column("password_hash", sa.String(length=60), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.users.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id"),
        schema="user",
    )

    op.create_table(
        "user_emails",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("verified_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.users.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="user",
    )

    op.create_index(
        "inx_uue_email_not_revoked_unq",
        "user_emails",
        ["email"],
        unique=True,
        schema="user",
        postgresql_where=sa.text("revoked_at IS NULL"),
    )
    op.create_index(
        "inx_uue_user_id",
        "user_emails",
        ["user_id"],
        unique=False,
        schema="user",
    )
    op.create_index(
        "inx_uue_user_id_is_primary_unq",
        "user_emails",
        ["user_id"],
        unique=True,
        schema="user",
        postgresql_where=sa.text("is_primary IS true AND revoked_at IS NULL"),
    )

    op.create_table(
        "user_sessions",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
            comment="The flag changes its state when the 'AUTHORIZATION' type session is explicitly deleted. "
            "The expiration of the session lifetime is not reflected in the table, "
            "redis ttl is responsible for this.",
        ),
        sa.Column("created_ip", postgresql.INET(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="user",
    )

    op.create_index(
        "inx_uus_user_id_created_at_desc",
        "user_sessions",
        ["user_id", sa.literal_column("created_at DESC")],
        unique=False,
        schema="user",
    )
    op.create_index(
        "inx_uus_user_id_is_deleted_false",
        "user_sessions",
        ["user_id"],
        unique=False,
        schema="user",
        postgresql_where=sa.text("is_deleted IS false"),
    )


def downgrade() -> None:
    op.drop_index(
        "inx_uus_user_id_is_deleted_false",
        table_name="user_sessions",
        schema="user",
        postgresql_where=sa.text("is_deleted IS false"),
    )
    op.drop_index(
        "inx_uus_user_id_created_at_desc",
        table_name="user_sessions",
        schema="user",
    )
    op.drop_table("user_sessions", schema="user")
    op.drop_index(
        "inx_uue_user_id_is_primary_unq",
        table_name="user_emails",
        schema="user",
        postgresql_where=sa.text("is_primary IS true AND revoked_at IS NULL"),
    )
    op.drop_index("inx_uue_user_id", table_name="user_emails", schema="user")
    op.drop_index(
        "inx_uue_email_not_revoked_unq",
        table_name="user_emails",
        schema="user",
        postgresql_where=sa.text("revoked_at IS NULL"),
    )
    op.drop_table("user_emails", schema="user")
    op.drop_table("user_credentials", schema="user")
    op.drop_index(
        "inx_uuat_long_token_hash_active",
        table_name="user_action_tokens",
        schema="user",
        postgresql_where=sa.text("status = 'active'"),
    )
    op.drop_index(
        "inx_uuat_user_id_kind_status_active_unq",
        table_name="user_action_tokens",
        schema="user",
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )
    op.drop_index(
        "inx_uuat_user_id_created_at_desc",
        table_name="user_action_tokens",
        schema="user",
    )
    op.drop_table("user_action_tokens", schema="user")
    op.drop_index(
        "inx_uu_status_until_at_blocked",
        table_name="users",
        schema="user",
        postgresql_where=sa.text("status = 'TEMPORARY_BLOCKED'"),
    )
    op.drop_table("users", schema="user")

    user_status_type.drop(op.get_bind())
    user_auth_token_kind_type.drop(op.get_bind())
    user_action_token_status_type.drop(op.get_bind())
    user_action_token_channel_type.drop(op.get_bind())

    op.execute('drop schema if exists "user" cascade;')
