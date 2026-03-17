from typing import TYPE_CHECKING

from config.runtime.loader import get_config
from context.user.application.dtos.command.auth import UserRegisterCommand
from context.user.application.dtos.data.user import UserCreateData
from context.user.application.dtos.entity.user import UserDTO, UserMeDTO
from context.user.application.dtos.entity.user_action_token import (
    UserActionTokenDTO,
    UserActionTokenGeneratedDTO,
)
from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.dtos.result.auth import UserRegisterResult
from context.user.application.dtos.result.user_session import (
    UserSessionCreateResult,
)
from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
)
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.errors.user_email import UserEmailAlreadyExistsError
from context.user.application.mapping.audit.confirm_email import (
    map_request_confirm_email_success,
)
from context.user.application.mapping.audit.login import map_login_event_from_register
from context.user.application.mapping.audit.register import (
    map_register_event_failure,
    map_register_event_success,
)
from context.user.application.mapping.user import (
    map_register_user_data_to_user_me,
)
from context.user.application.services import (
    user_action_token_service,
    user_credentials_service,
    user_email_service,
    user_flow_session_service,
    user_service,
    user_session_service,
)
from context.user.infra.gateways.email import user_email_agent
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db
from shared.utils.background_tasks import schedule_in_background

if TYPE_CHECKING:
    from context.user.application.types.auth import UserRegisterStatus
    from infra.audit.dtos import AuditEventCommand


async def register_user(
    command: UserRegisterCommand,
) -> UserRegisterResult:
    """Регистрация пользователя.

    Raises:
        UserEmailAlreadyExistsError: Если email существует и отключен режим сокрытия
            существования email.
    """
    config = get_config()
    auth_cfg = config.context.user.authorization

    try:
        user_data = UserCreateData(
            name=command.name,
            locale=command.locale,
            timezone=command.timezone,
        )

        auth_session: UserSessionCreateResult | None = None

        async with db.transaction():
            user = await user_service.create_user(user_data)
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

            if not auth_cfg.login_requires_verified_email:
                auth_session = await user_session_service.create_session(
                    user_id=user.id,
                    ip_address=command.ip_address,
                )
    except UserEmailAlreadyExistsError:
        if not auth_cfg.hide_email_existence_on_register:
            await audit_api.record_events(map_register_event_failure(command))
            raise
        return await _handle_hidden_duplicate_registration(command)

    return await _finalize_registration(
        command=command,
        user=user,
        user_email=user_email,
        action_token=action_token,
        action_token_generated=action_token_generated,
        auth_session=auth_session,
    )


async def _handle_hidden_duplicate_registration(
    command: UserRegisterCommand,
) -> UserRegisterResult:
    # Инициализируем flow session с `user_id=None` для имитации успешной регистрации.
    flow_session = await user_flow_session_service.create_flow_session(
        user_id=None,
        kind=UserFlowSessionKind.EMAIL_VERIFICATION,
    )

    await audit_api.record_events(
        map_register_event_failure(command, flow_session.storage),
    )

    return UserRegisterResult(
        user=None,
        auth_session=None,
        flow_session=flow_session,
        status="email_verification_required",
    )


async def _finalize_registration(
    command: UserRegisterCommand,
    *,
    user: UserDTO,
    user_email: UserEmailDTO,
    action_token: UserActionTokenDTO,
    action_token_generated: UserActionTokenGeneratedDTO,
    auth_session: UserSessionCreateResult | None,
) -> UserRegisterResult:
    user_me: UserMeDTO | None = None
    status: UserRegisterStatus = "email_verification_required"

    flow_session = await user_flow_session_service.create_flow_session(
        user_id=user.id,
        kind=UserFlowSessionKind.EMAIL_VERIFICATION,
    )

    await schedule_in_background(
        user_email_agent.send_email_verification_email(
            user_email=user_email,
            action_token=action_token,
            token_generated=action_token_generated,
        ),
    )

    audit_events: list[AuditEventCommand] = [
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
    ]

    if auth_session is not None:
        audit_events.append(
            map_login_event_from_register(
                command=command,
                user=user,
                auth_session=auth_session.storage,
            ),
        )

    await audit_api.record_events(*audit_events)

    if auth_session is not None:
        user_me = map_register_user_data_to_user_me(
            user,
            user_email,
        )
        status = "logged_in"

    return UserRegisterResult(
        user=user_me,
        auth_session=auth_session,
        flow_session=flow_session,
        status=status,
    )
