import uuid

from context.user.application.enums.user_session import UserSessionKind
from context.user.application.services import user_session_service
from infra.persistence.postgresql.connection import db


async def logout(session_id: uuid.UUID) -> None:
    async with db.transaction():
        await user_session_service.delete_session(
            session_id=session_id,
            kind=UserSessionKind.AUTHORIZATION,
        )
