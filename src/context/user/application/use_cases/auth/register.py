from context.user.application.dtos.command.auth import UserRegisterCommand
from context.user.application.dtos.payload.user import UserCreatePayload
from context.user.application.dtos.result.auth import UserRegisterResult
from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
)
from context.user.application.enums.user_session import UserSessionKind
from context.user.application.errors.user_email import UserEmailAlreadyExistsError
from context.user.application.mapping.audit.register import (
    map_register_event_failure,
    map_register_event_success,
)
from context.user.application.services import (
    user_action_token_service,
    user_credentials_service,
    user_email_service,
    user_service,
    user_session_service,
)
from context.user.infra.gateways.email import user_email_agent
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db
from shared.utils.asyncio_utils import run_in_background


async def register_user(
    command: UserRegisterCommand,
) -> UserRegisterResult:
    """Register user.

    Raises:
        UserEmailAlreadyExistsError
    """
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
            session = await user_session_service.create_session(
                user_id=user.id,
                kind=UserSessionKind.EMAIL_VERIFICATION,
                ip_address=command.ip_address,
            )
    except UserEmailAlreadyExistsError:
        await audit_api.record_event_in_new_tx(map_register_event_failure(command))
        raise

    run_in_background(
        user_email_agent.send_user_registration_email(
            email=user_email,
            token=action_token,
            token_generated=action_token_generated,
        ),
    )

    await audit_api.record_event_in_new_tx(
        map_register_event_success(
            command=command,
            user=user,
            email=user_email,
            action_token=action_token,
            session=session.storage,
        ),
    )

    return UserRegisterResult(
        user=user,
        session=session,
        status="email_verification_required",
    )
