from typing import TYPE_CHECKING

from config import config
from context.user.application.dtos.command.auth import UserPasswordResetCommand
from context.user.application.dtos.result.auth import UserPasswordResetResult
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.errors.auth import PasswordResetSessionNotConfirmedError
from context.user.application.mapping.audit.confirm_password import (
    map_password_reset_failure,
    map_password_reset_success,
)
from context.user.application.services import (
    user_credentials_service,
    user_flow_session_service,
    user_session_service,
)
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db

if TYPE_CHECKING:
    from context.user.application.dtos.result.user_session import (
        UserSessionCreateResult,
    )


async def password_reset(command: UserPasswordResetCommand) -> UserPasswordResetResult:
    """Set new password.

    Raises:
        PasswordResetSessionNotConfirmedError
    """
    if not command.flow_session.is_confirmed or command.flow_session.user_id is None:
        ex = PasswordResetSessionNotConfirmedError()
        await audit_api.record_events(map_password_reset_failure(command, ex))
        raise ex

    auth_session: UserSessionCreateResult | None = None

    async with db.transaction():
        await user_credentials_service.set_new_password(
            user_id=command.flow_session.user_id,
            password=command.password.get_secret_value(),
        )

        if config.context.user.password_reset.auto_login_on_success:
            auth_session = await user_session_service.create_session(
                user_id=command.flow_session.user_id,
                ip_address=command.ip_address,
            )

    await user_flow_session_service.delete_flow_session(
        session_id=command.flow_session.session_id,
        kind=UserFlowSessionKind.PASSWORD_RESET,
    )

    await audit_api.record_events(
        map_password_reset_success(
            command=command,
            auth_session=(auth_session.storage if auth_session is not None else None),
        ),
    )

    return UserPasswordResetResult(auth_session=auth_session)
