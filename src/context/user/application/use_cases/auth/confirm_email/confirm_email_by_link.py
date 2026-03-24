from config.runtime.loader import get_config
from context.user.application.dtos.command.auth import UserConfirmEmailByLinkCommand
from context.user.application.dtos.entity.user_action_token import UserActionTokenDTO
from context.user.application.dtos.result.auth import UserActionConfirmResult
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
from context.user.application.mapping.audit.login import map_login_event_from_flow
from context.user.application.services import (
    user_action_token_service,
    user_auth_service,
    user_email_service,
    user_flow_session_service,
)
from infra.audit import audit_api
from infra.audit.dtos import AuditEventCommand
from infra.persistence.postgresql.connection import db


async def confirm_email_by_link(
    command: UserConfirmEmailByLinkCommand,
) -> UserActionConfirmResult:
    """Подтвердить email по ссылке.

    Raises:
        InvalidUserActionTokenError
        UserEmailNotFoundError
    """
    config = get_config()

    try:
        async with db.transaction():
            action_token = await user_action_token_service.verify_link_token(
                token=command.token,
                kind=UserActionTokenKind.EMAIL_VERIFICATION,
            )

            if action_token.channel != UserActionTokenChannelType.EMAIL:
                raise RuntimeError("EMAIL_VERIFICATION token must use EMAIL channel")

            user_email = await user_email_service.verify_email(
                email_id=action_token.channel_id,
            )

            if command.flow_session is not None:
                await user_flow_session_service.delete_flow_session(
                    session_id=command.flow_session.session_id,
                    kind=UserFlowSessionKind.EMAIL_VERIFICATION,
                )

            result = await user_auth_service.build_user_action_confirm_result(
                action_token=action_token,
                ip_address=command.ip_address,
                auto_login_on_success=(
                    config.context.user.email_verification.auto_login_on_success
                    and user_email.is_primary
                ),
            )
    except InvalidUserActionTokenError as ex:
        await audit_api.record_events(
            map_confirm_email_by_link_failure(command, ex),
        )
        raise

    await audit_api.record_events(*_build_audit_events(command, action_token, result))

    return result


def _build_audit_events(
    command: UserConfirmEmailByLinkCommand,
    action_token: UserActionTokenDTO,
    result: UserActionConfirmResult,
) -> list[AuditEventCommand]:
    auth_session = (
        result.auth_session.storage if result.auth_session is not None else None
    )

    events: list[AuditEventCommand] = [
        map_confirm_email_by_link_success(
            command=command,
            action_token=action_token,
            auth_session=auth_session,
        ),
    ]

    if auth_session is not None and result.user_me is not None:
        events.append(
            map_login_event_from_flow(
                user_me=result.user_me,
                auth_session=auth_session,
                ip_address=command.ip_address,
            ),
        )

    return events
