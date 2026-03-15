from typing import TYPE_CHECKING

from config import config
from context.user.application.dtos.command.auth import UserConfirmEmailByLinkCommand
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
    map_confirm_email_by_link_failure,
    map_confirm_email_by_link_success,
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


async def confirm_email_by_link(
    command: UserConfirmEmailByLinkCommand,
) -> UserConfirmEmailResult:
    """Confirm user email by link.

    Raises:
        InvalidUserActionTokenError
        UserEmailNotFoundError
    """
    auth_session: UserSessionCreateResult | None = None

    try:
        async with db.transaction():
            action_token = await user_action_token_service.verify_link_token(
                token=command.token,
                kind=UserActionTokenKind.EMAIL_VERIFICATION,
            )

            if action_token.channel != UserActionTokenChannelType.EMAIL:
                raise RuntimeError("EMAIL_VERIFICATION token must use EMAIL channel")

            email = await user_email_service.verify_email(
                email_id=action_token.channel_id,
            )

            if command.flow_session is not None:
                await user_flow_session_service.delete_flow_session(
                    session_id=command.flow_session.session_id,
                    kind=UserFlowSessionKind.EMAIL_VERIFICATION,
                )

            if (
                config.context.user.email_verification.auto_login_on_success
                and email.is_primary
            ):
                auth_session = await user_session_service.create_session(
                    user_id=action_token.user_id,
                    ip_address=command.ip_address,
                )
    except InvalidUserActionTokenError as ex:
        await audit_api.record_events(
            map_confirm_email_by_link_failure(command, ex),
        )
        raise

    await audit_api.record_events(
        map_confirm_email_by_link_success(
            command=command,
            action_token=action_token,
            auth_session=(auth_session.storage if auth_session is not None else None),
        ),
    )

    return UserConfirmEmailResult(auth_session=auth_session)
