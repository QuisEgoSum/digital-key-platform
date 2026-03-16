from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert

from context.user.infra.models import UserCredentialsRow
from infra.persistence.postgresql.connection import db
from shared.utils.datetime_utils import current_datetime


async def insert_user_credentials(
    user_id: int,
    password_hash: str,
) -> None:
    stmt = insert(UserCredentialsRow).values(
        user_id=user_id,
        password_hash=password_hash,
    )
    await db.execute(stmt)


async def set_new_password(
    user_id: int,
    password_hash: str,
) -> None:
    stmt = (
        update(UserCredentialsRow)
        .values(
            password_hash=password_hash,
            password_changed_at=current_datetime(),
        )
        .where(UserCredentialsRow.user_id == user_id)
    )
    await db.execute(stmt)
