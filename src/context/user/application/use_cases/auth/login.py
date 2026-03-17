from typing import TYPE_CHECKING

from config.runtime.loader import get_config
from context.user.application.dtos.command.auth import UserLoginCommand
from context.user.application.dtos.result.auth import UserLoginResult
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.mapping.audit.login import (
    map_login_event_anonymous_failure,
    map_login_event_identified_failure,
    map_login_event_success,
)
from context.user.application.mapping.user import map_login_details_to_user_me
from context.user.application.services import (
    user_credentials_service,
    user_flow_session_service,
    user_service,
    user_session_service,
)
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db
from shared.errors.base import ApplicationError

if TYPE_CHECKING:
    from context.user.application.dtos.entity.user import UserLoginDetailsDTO
    from context.user.application.dtos.entity.user_flow_session import (
        UserFlowSessionEmailVerificationDTO,
    )
    from context.user.application.dtos.result.user_flow_session import (
        UserFlowSessionCreateResult,
    )
    from context.user.application.dtos.result.user_session import (
        UserSessionCreateResult,
    )
    from context.user.application.types.auth import UserLoginStatus


async def login(command: UserLoginCommand) -> UserLoginResult:
    """User login.

    Raises:
        InvalidCredentialsError
        UserBannedError
        UserTemporaryBlockedError
    """
    config = get_config()
    auth_config = config.context.user.authorization

    login_details: UserLoginDetailsDTO | None = None
    auth_session: UserSessionCreateResult | None = None
    flow_session: (
        UserFlowSessionCreateResult[UserFlowSessionEmailVerificationDTO] | None
    ) = None
    status: UserLoginStatus

    try:

        async with db.transaction():
            login_details = await user_service.get_login_details(email=command.email)

            await user_credentials_service.verify_user_credentials(
                login_details=login_details,
                password=command.password.get_secret_value(),
            )

            user_service.verify_login_allowed(login_details)

            if (
                auth_config.login_requires_verified_email
                and not login_details.is_verified_primary_email
            ):
                status = "email_verification_required"
                flow_session = await user_flow_session_service.create_flow_session(
                    user_id=login_details.id,
                    kind=UserFlowSessionKind.EMAIL_VERIFICATION,
                )
            else:
                status = "logged_in"
                auth_session = await user_session_service.create_session(
                    user_id=login_details.id,
                    ip_address=command.ip_address,
                )
    except ApplicationError as ex:
        if login_details is None:
            audit = map_login_event_anonymous_failure(command, ex)
        else:
            audit = map_login_event_identified_failure(command, login_details, ex)

        await audit_api.record_events(audit)

        raise

    await audit_api.record_events(
        map_login_event_success(
            command=command,
            login_details=login_details,
            auth_session=auth_session.storage if auth_session is not None else None,
            flow_session=flow_session.storage if flow_session is not None else None,
            status=status,
        ),
    )

    return UserLoginResult(
        user=map_login_details_to_user_me(login_details),
        auth_session=auth_session,
        flow_session=flow_session,
        status=status,
    )
