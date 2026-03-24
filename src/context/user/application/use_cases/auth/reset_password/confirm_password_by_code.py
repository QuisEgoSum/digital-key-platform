from context.user.application.dtos.command.auth import UserConfirmPasswordByCodeCommand
from context.user.application.enums.user_action_token import UserActionTokenKind
from context.user.application.errors.user_action_token import (
    InvalidUserActionTokenError,
)
from context.user.application.mapping.audit.confirm_password import (
    map_confirm_password_by_code_failure,
    map_confirm_password_by_code_success,
)
from context.user.application.services import (
    user_action_token_service,
    user_flow_session_service,
)
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db


async def confirm_password_by_code(command: UserConfirmPasswordByCodeCommand) -> None:
    """Подтвердить сброс пароля по коду.

    Raises:
        InvalidUserActionTokenError
    """
    if command.flow_session.is_confirmed:
        return
    if command.flow_session.user_id is None:
        ex = InvalidUserActionTokenError("flow_session_not_bound")
        await audit_api.record_events(
            map_confirm_password_by_code_failure(command, ex),
        )
        raise ex

    try:
        async with db.transaction():
            action_token = await user_action_token_service.verify_short_token(
                token=command.token,
                user_id=command.flow_session.user_id,
                kind=UserActionTokenKind.PASSWORD_RESET,
            )

            command.flow_session.is_confirmed = True

            await user_flow_session_service.update_flow_session_data(
                command.flow_session,
            )
    except InvalidUserActionTokenError as ex:
        await audit_api.record_events(
            map_confirm_password_by_code_failure(command, ex),
        )
        raise

    await audit_api.record_events(
        map_confirm_password_by_code_success(command, action_token),
    )
