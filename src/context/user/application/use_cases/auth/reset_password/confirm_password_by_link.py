from typing import TYPE_CHECKING

from context.user.application.dtos.command.auth import UserConfirmPasswordByLinkCommand
from context.user.application.dtos.result.auth import UserConfirmPasswordResult
from context.user.application.enums.user_action_token import UserActionTokenKind
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.errors.user_action_token import (
    InvalidUserActionTokenError,
)
from context.user.application.mapping.audit.confirm_password import (
    map_confirm_password_by_link_failure,
    map_confirm_password_by_link_success,
)
from context.user.application.services import (
    user_action_token_service,
    user_flow_session_service,
)
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db

if TYPE_CHECKING:
    from context.user.application.dtos.entity.user_flow_session import (
        UserFlowSessionPasswordResetDTO,
    )
    from context.user.application.dtos.result.user_flow_session import (
        UserFlowSessionCreateResult,
    )


async def confirm_password_by_link(
    command: UserConfirmPasswordByLinkCommand,
) -> UserConfirmPasswordResult:
    """Confirm password reset by link.

    Creates a PASSWORD_RESET session with the confirmation flag set, if there is none.

    Raises:
        InvalidUserActionTokenError
    """
    created_flow_session: (
        UserFlowSessionCreateResult[UserFlowSessionPasswordResetDTO] | None
    ) = None
    flow_session: UserFlowSessionPasswordResetDTO | None = command.flow_session

    try:
        async with db.transaction():
            action_token = await user_action_token_service.verify_link_token(
                token=command.token,
                kind=UserActionTokenKind.PASSWORD_RESET,
            )

            if command.flow_session is not None:
                command.flow_session.is_confirmed = True
                await user_flow_session_service.update_flow_session_data(
                    command.flow_session,
                )
            else:
                created_flow_session = (
                    await user_flow_session_service.create_flow_session(
                        user_id=action_token.user_id,
                        kind=UserFlowSessionKind.PASSWORD_RESET,
                        is_confirmed=True,
                    )
                )
                flow_session = created_flow_session.storage
    except InvalidUserActionTokenError as ex:
        await audit_api.record_events(
            map_confirm_password_by_link_failure(
                command=command,
                error=ex,
            ),
        )
        raise

    if flow_session is None:
        raise RuntimeError("Session object is required")

    await audit_api.record_events(
        map_confirm_password_by_link_success(
            command=command,
            action_token=action_token,
            flow_session=flow_session,
        ),
    )

    return UserConfirmPasswordResult(created_flow_session=created_flow_session)
