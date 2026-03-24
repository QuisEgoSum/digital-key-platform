from config.runtime.loader import get_config
from context.user.application.dtos.command.auth import UserRequestPasswordResetCommand
from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.dtos.entity.user_flow_session import (
    UserFlowSessionPasswordResetDTO,
)
from context.user.application.dtos.result.auth import UserRequestPasswordResetResult
from context.user.application.dtos.result.user_flow_session import (
    UserFlowSessionCreateResult,
)
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
from shared.utils.background_tasks import schedule_in_background


async def request_password_reset(
    command: UserRequestPasswordResetCommand,
) -> UserRequestPasswordResetResult:
    """Запросить сброс пароля.

    Raises:
        UserEmailNotFoundError: Если email не существует и отключен режим сокрытия
            существования email.
        UserEmailNotPrimaryError: Если email не является основным и отключен режим сокрытия
            существования email.
    """
    config = get_config()
    reset_config = config.context.user.password_reset

    user_email: UserEmailDTO | None = None

    try:
        async with db.transaction():
            user_email = await user_email_service.get_email(command.email)

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

            flow_session, created_flow_session = await _ensure_flow_session(
                existing_flow_session=command.flow_session,
                user_id=user_email.user_id,
            )
    except ApplicationError as ex:
        return await _handle_error(
            command=command,
            hide_email_existence_on_request=(
                reset_config.hide_email_existence_on_request
            ),
            error=ex,
            user_email=user_email,
            flow_session=command.flow_session,
        )

    await schedule_in_background(
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

    return UserRequestPasswordResetResult(
        created_flow_session=created_flow_session,
    )


async def _ensure_flow_session(
    *,
    existing_flow_session: UserFlowSessionPasswordResetDTO | None,
    user_id: int,
) -> tuple[
    UserFlowSessionPasswordResetDTO,
    UserFlowSessionCreateResult[UserFlowSessionPasswordResetDTO] | None,
]:
    if existing_flow_session is None or existing_flow_session.user_id != user_id:
        created_flow_session = await user_flow_session_service.create_flow_session(
            user_id=user_id,
            kind=UserFlowSessionKind.PASSWORD_RESET,
            is_confirmed=False,
        )
        return created_flow_session.storage, created_flow_session

    await user_flow_session_service.update_flow_session_expire(
        session_id=existing_flow_session.session_id,
        kind=existing_flow_session.kind,
    )
    return existing_flow_session, None


async def _handle_error(
    command: UserRequestPasswordResetCommand,
    *,
    hide_email_existence_on_request: bool,
    error: ApplicationError,
    user_email: UserEmailDTO | None,
    flow_session: UserFlowSessionPasswordResetDTO | None,
) -> UserRequestPasswordResetResult:
    if not hide_email_existence_on_request:
        await audit_api.record_events(
            map_request_password_reset_failure(
                command=command,
                user_email=user_email,
                flow_session=flow_session,
                error=error,
            ),
        )
        raise

    is_suppressed_error = isinstance(
        error,
        (UserEmailNotPrimaryError, UserEmailNotFoundError),
    )

    created_flow_session: (
        UserFlowSessionCreateResult[UserFlowSessionPasswordResetDTO] | None
    ) = None

    if is_suppressed_error and (
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
            error=error,
        ),
    )

    if is_suppressed_error:
        return UserRequestPasswordResetResult(
            created_flow_session=created_flow_session,
        )

    raise
