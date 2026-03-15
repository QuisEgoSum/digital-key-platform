from context.user.application.dtos.command.auth import UserLogoutCommand
from context.user.application.mapping.audit.logout import map_logout_event
from context.user.application.services import user_session_service
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db


async def logout(command: UserLogoutCommand) -> None:
    async with db.transaction():
        await user_session_service.delete_session(
            session_id=command.session.session_id,
        )

    await audit_api.record_events(map_logout_event(command))
