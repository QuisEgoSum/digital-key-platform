from typing import TYPE_CHECKING

from config import config
from context.user.application.dtos.command.auth import UserConfirmEmailByCodeCommand
from context.user.application.dtos.result.auth import UserConfirmEmailResult
from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
)
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.errors.user_action_token import (
    InvalidUserActionTokenError,
)
from context.user.application.mapping.audit.confirm_email import (
    map_confirm_email_by_code_failure,
    map_confirm_email_by_code_success,
)
from context.user.application.services import (
    user_action_token_service,
    user_email_service,
    user_flow_session_service,
    user_session_service,
)
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db

if TYPE_CHECKING:
    from context.user.application.dtos.result.user_session import (
        UserSessionCreateResult,
    )


async def confirm_email_by_code(
    command: UserConfirmEmailByCodeCommand,
) -> UserConfirmEmailResult:
    """Confirm user email by code.

    Raises:
        InvalidUserActionTokenError
        UserEmailNotFoundError
    """
    if command.flow_session.user_id is None:
        ex = InvalidUserActionTokenError("flow_session_not_bound")
        await audit_api.record_events(
            map_confirm_email_by_code_failure(command, ex),
        )
        raise ex

    auth_session: UserSessionCreateResult | None = None

    try:
        async with db.transaction():
            action_token = await user_action_token_service.verify_short_token(
                token=command.token,
                user_id=command.flow_session.user_id,
                kind=UserActionTokenKind.EMAIL_VERIFICATION,
            )

            if action_token.channel != UserActionTokenChannelType.EMAIL:
                raise RuntimeError("EMAIL_VERIFICATION token must use EMAIL channel")

            user_email = await user_email_service.verify_email(
                email_id=action_token.channel_id,
            )

            if (
                config.context.user.email_verification.auto_login_on_success
                and user_email.is_primary
            ):
                auth_session = await user_session_service.create_session(
                    user_id=command.flow_session.user_id,
                    ip_address=command.ip_address,
                )
    except InvalidUserActionTokenError as ex:
        await audit_api.record_events(
            map_confirm_email_by_code_failure(command, ex),
        )
        raise

    await user_flow_session_service.delete_flow_session(
        session_id=command.flow_session.session_id,
        kind=UserFlowSessionKind.EMAIL_VERIFICATION,
    )

    await audit_api.record_events(
        map_confirm_email_by_code_success(
            command=command,
            action_token=action_token,
            auth_session=(auth_session.storage if auth_session is not None else None),
        ),
    )

    return UserConfirmEmailResult(auth_session=auth_session)
