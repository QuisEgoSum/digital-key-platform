from context.user.application.dtos.command.auth import UserRegisterCommand
from context.user.application.dtos.payload.user import UserCreatePayload
from context.user.application.dtos.result.auth import UserRegisterResult
from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
)
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.errors.user_email import UserEmailAlreadyExistsError
from context.user.application.mapping.audit.confirm_email import (
    map_request_confirm_email_success,
)
from context.user.application.mapping.audit.register import (
    map_register_event_failure,
    map_register_event_success,
)
from context.user.application.services import (
    user_action_token_service,
    user_credentials_service,
    user_email_service,
    user_flow_session_service,
    user_service,
)
from context.user.infra.gateways.email import user_email_agent
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db
from shared.utils.asyncio_utils import run_in_background


async def register_user(
    command: UserRegisterCommand,
) -> UserRegisterResult:
    """Register user."""
    user_payload = UserCreatePayload(
        name=command.name,
        locale=command.locale,
        timezone=command.timezone,
    )

    try:
        async with db.transaction():
            user = await user_service.create_user(user_payload)
            user_email = await user_email_service.create_user_email(
                user_id=user.id,
                email=command.email,
                is_primary=True,
            )
            await user_credentials_service.create_user_credential(
                user_id=user.id,
                password=command.password.get_secret_value(),
            )
            action_token, action_token_generated = (
                await user_action_token_service.create_action_token(
                    user_id=user.id,
                    kind=UserActionTokenKind.EMAIL_VERIFICATION,
                    channel=UserActionTokenChannelType.EMAIL,
                    channel_id=user_email.id,
                )
            )
    except UserEmailAlreadyExistsError:
        # Do not reveal whether the email already exists.
        # We intentionally mimic the successful registration flow by returning
        # "email_verification_required" and creating a flow session (without user_id).
        # This keeps the observable behavior identical and prevents account enumeration.
        flow_session = await user_flow_session_service.create_flow_session(
            user_id=None,
            kind=UserFlowSessionKind.EMAIL_VERIFICATION,
        )
        await audit_api.record_events(
            map_register_event_failure(command, flow_session.storage),
        )
        return UserRegisterResult(
            flow_session=flow_session,
            status="email_verification_required",
        )

    flow_session = await user_flow_session_service.create_flow_session(
        user_id=user.id,
        kind=UserFlowSessionKind.EMAIL_VERIFICATION,
    )

    run_in_background(
        user_email_agent.send_email_verification_email(
            user_email=user_email,
            action_token=action_token,
            token_generated=action_token_generated,
        ),
    )

    await audit_api.record_events(
        map_register_event_success(
            command=command,
            user=user,
            user_email=user_email,
            flow_session=flow_session.storage,
        ),
        map_request_confirm_email_success(
            user_id=user.id,
            ip_address=command.ip_address,
            user_email=user_email,
            action_token=action_token,
            flow_session=flow_session.storage,
        ),
    )

    return UserRegisterResult(
        flow_session=flow_session,
        status="email_verification_required",
    )
