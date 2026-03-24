from typing import TYPE_CHECKING

from context.user.application.dtos.entity.user_action_token import UserActionTokenDTO
from context.user.application.dtos.result.auth import UserActionConfirmResult
from context.user.application.services import user_service, user_session_service

if TYPE_CHECKING:
    from context.user.application.dtos.entity.user import UserMeDTO
    from context.user.application.dtos.result.user_session import (
        UserSessionCreateResult,
    )
    from context.user.application.types.auth import UserConfirmStatus


async def build_user_action_confirm_result(
    action_token: UserActionTokenDTO,
    ip_address: str | None,
    auto_login_on_success: bool,
) -> UserActionConfirmResult:
    status: UserConfirmStatus = "confirmed"
    user_me: UserMeDTO | None = None
    auth_session: UserSessionCreateResult | None = None

    if auto_login_on_success:
        status = "logged_in"
        user_me = await user_service.get_user_me(action_token.user_id)
        auth_session = await user_session_service.create_session(
            user_id=action_token.user_id,
            ip_address=ip_address,
        )

    return UserActionConfirmResult(
        status=status,
        user_me=user_me,
        auth_session=auth_session,
    )
