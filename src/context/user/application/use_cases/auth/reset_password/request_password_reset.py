from typing import TYPE_CHECKING

from context.user.application.dtos.command.auth import UserRequestPasswordResetCommand
from context.user.application.dtos.result.auth import UserRequestPasswordResetResult
from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
)
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.errors.user_email import (
    UserEmailNotFoundError,
    UserEmailNotPrimaryError,
)
from context.user.application.mapping.audit.confirm_password import (
    map_request_password_reset_failure,
    map_request_password_reset_success,
)
from context.user.application.services import (
    user_action_token_service,
    user_email_service,
    user_flow_session_service,
)
from context.user.infra.gateways.email import user_email_agent
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db
from shared.errors.base import ApplicationError
from shared.utils.asyncio_utils import run_in_background

if TYPE_CHECKING:
    from context.user.application.dtos.entity.user_email import UserEmailDTO
    from context.user.application.dtos.entity.user_flow_session import (
        UserFlowSessionPasswordResetDTO,
    )
    from context.user.application.dtos.result.user_flow_session import (
        UserFlowSessionCreateResult,
    )


async def request_password_reset(
    command: UserRequestPasswordResetCommand,
) -> UserRequestPasswordResetResult:
    """Request reset password email."""
    created_flow_session: (
        UserFlowSessionCreateResult[UserFlowSessionPasswordResetDTO] | None
    ) = None
    flow_session: UserFlowSessionPasswordResetDTO | None = command.flow_session
    user_email: UserEmailDTO | None = None

    try:
        async with db.transaction():
            user_email = await user_email_service.get_email(
                command.email,
            )

            if not user_email.is_primary:
                raise UserEmailNotPrimaryError()

            action_token, action_token_generated = (
                await user_action_token_service.create_action_token(
                    user_id=user_email.user_id,
                    kind=UserActionTokenKind.PASSWORD_RESET,
                    channel=UserActionTokenChannelType.EMAIL,
                    channel_id=user_email.id,
                )
            )

            # With retries, the session may already exist.
            if flow_session is None or flow_session.user_id != user_email.user_id:
                created_flow_session = (
                    await user_flow_session_service.create_flow_session(
                        user_id=action_token.user_id,
                        kind=UserFlowSessionKind.PASSWORD_RESET,
                        is_confirmed=False,
                    )
                )
                flow_session = created_flow_session.storage
            else:
                # We are re-specializing ttl in order not to violate the time limit
                # for performing actions within the flow.
                await user_flow_session_service.update_flow_session_expire(
                    session_id=flow_session.session_id,
                    kind=flow_session.kind,
                )
    except ApplicationError as ex:
        is_suppress_exception = isinstance(
            ex,
            (UserEmailNotPrimaryError, UserEmailNotFoundError),
        )

        if is_suppress_exception and (
            flow_session is None or flow_session.user_id is not None
        ):
            created_flow_session = await user_flow_session_service.create_flow_session(
                user_id=None,
                kind=UserFlowSessionKind.PASSWORD_RESET,
                is_confirmed=False,
            )
            flow_session = created_flow_session.storage

        await audit_api.record_events(
            map_request_password_reset_failure(
                command=command,
                user_email=user_email,
                flow_session=flow_session,
                error=ex,
            ),
        )

        if is_suppress_exception:
            return UserRequestPasswordResetResult(
                created_flow_session=created_flow_session,
            )
        raise

    run_in_background(
        user_email_agent.send_user_password_reset_email(
            user_email=user_email,
            action_token=action_token,
            token_generated=action_token_generated,
        ),
    )

    await audit_api.record_events(
        map_request_password_reset_success(
            command=command,
            user_email=user_email,
            action_token=action_token,
            flow_session=flow_session,
        ),
    )

    return UserRequestPasswordResetResult(created_flow_session=created_flow_session)
