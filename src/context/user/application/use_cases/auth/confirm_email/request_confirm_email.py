from context.user.application.dtos.command.auth import UserRequestConfirmEmailCommand
from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
)
from context.user.application.mapping.audit.confirm_email import (
    map_request_confirm_email_success,
    map_request_confirm_email_suppressed,
)
from context.user.application.services import (
    user_action_token_service,
    user_email_service,
)
from context.user.infra.gateways.email import user_email_agent
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db
from shared.utils.asyncio_utils import run_in_background


async def request_confirm_email(command: UserRequestConfirmEmailCommand) -> None:
    """Request confirm email.

    Raises:
        UserEmailNotFoundError
    """
    if command.flow_session.user_id is None:
        await audit_api.record_events(
            map_request_confirm_email_suppressed(
                ip_address=command.ip_address,
                flow_session=command.flow_session,
            ),
        )
        return

    async with db.transaction():
        user_email = await user_email_service.get_user_primary_email(
            command.flow_session.user_id,
        )
        action_token, action_token_generated = (
            await user_action_token_service.create_action_token(
                user_id=command.flow_session.user_id,
                kind=UserActionTokenKind.EMAIL_VERIFICATION,
                channel=UserActionTokenChannelType.EMAIL,
                channel_id=user_email.id,
            )
        )

    run_in_background(
        user_email_agent.send_email_verification_email(
            user_email=user_email,
            action_token=action_token,
            token_generated=action_token_generated,
        ),
    )

    await audit_api.record_events(
        map_request_confirm_email_success(
            user_id=command.flow_session.user_id,
            ip_address=command.ip_address,
            user_email=user_email,
            action_token=action_token,
            flow_session=command.flow_session,
        ),
    )
