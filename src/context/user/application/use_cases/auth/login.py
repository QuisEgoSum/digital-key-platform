from typing import TYPE_CHECKING

from context.user.application.dtos.command.auth import UserLoginCommand
from context.user.application.dtos.result.auth import UserLoginResult
from context.user.application.enums.user_session import UserSessionKind
from context.user.application.mapping.audit.login import (
    map_login_event_anonymous,
    map_login_event_with_error,
    map_login_event_with_session,
)
from context.user.application.mapping.user import map_login_details_to_user_me
from context.user.application.services import (
    user_credentials_service,
    user_service,
    user_session_service,
)
from infra.audit import audit_api
from infra.persistence.postgresql.connection import db
from shared.errors.base import ApplicationError

if TYPE_CHECKING:
    from context.user.application.dtos.entity.user import UserLoginDetailsDTO
    from context.user.application.types.auth import UserLoginStatus


async def login(command: UserLoginCommand) -> UserLoginResult:
    """User login.

    Raises:
        InvalidCredentialsError
        UserBannedError
        UserTemporaryBannedError
    """
    login_details: UserLoginDetailsDTO | None = None
    try:
        async with db.transaction():
            login_details = await user_service.get_login_details(email=command.email)

            await user_credentials_service.verify_user_credentials(
                login_details=login_details,
                password=command.password.get_secret_value(),
            )

            user_service.verify_login_allowed(login_details)

            if login_details.is_verified_primary_email:
                status: UserLoginStatus = "logged_in"
                session = await user_session_service.create_session(
                    user_id=login_details.id,
                    kind=UserSessionKind.AUTHORIZATION,
                    ip_address=command.ip_address,
                )
            else:
                status = "email_verification_required"
                session = await user_session_service.create_session(
                    user_id=login_details.id,
                    kind=UserSessionKind.EMAIL_VERIFICATION,
                    ip_address=command.ip_address,
                )
    except ApplicationError as ex:
        if login_details is None:
            audit = map_login_event_anonymous(command, ex)
        else:
            audit = map_login_event_with_error(command, login_details, ex)

        await audit_api.record_event_in_new_tx(audit)

        raise

    await audit_api.record_event_in_new_tx(
        map_login_event_with_session(command, login_details, session.storage, status),
    )

    return UserLoginResult(
        user=map_login_details_to_user_me(login_details),
        session=session,
        status=status,
    )
