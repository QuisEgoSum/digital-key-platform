from sqlalchemy.dialects.postgresql import insert

from context.user.infra.models import UserCredentialsRow
from infra.persistence.postgresql.connection import db


async def insert_user_credentials(
    user_id: int,
    password_hash: str,
) -> None:
    stmt = insert(UserCredentialsRow).values(
        user_id=user_id,
        password_hash=password_hash,
    )
    await db.execute(stmt)
