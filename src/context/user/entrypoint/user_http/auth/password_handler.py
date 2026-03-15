from sanic import Blueprint, HTTPResponse, empty

from config import config
from context.user.application import use_cases
from context.user.application.dtos.command.auth import (
    UserConfirmPasswordByCodeCommand,
    UserConfirmPasswordByLinkCommand,
)
from context.user.application.dtos.input.auth import (
    UserActionTokenInput,
)
from context.user.application.errors.user_action_token import (
    InvalidUserActionTokenError,
)
from infra import openapi
from infra.sanic import validator
from infra.sanic.http.request import AppRequest
from infra.sanic.security.user_auth import (
    UserFlowSessionPasswordResetDTO,
    inject_password_reset_session,
    load_password_reset_session,
)
from infra.sanic.utils.request import get_request_ip_address
from infra.sanic.utils.responses import add_cookie

router = Blueprint("UserAuthPasswordRouter")


@router.post("/auth/password/verify")
@openapi.tag("User Auth Reset Password")
@openapi.no_content()
@openapi.errors(InvalidUserActionTokenError)
@validator.body(UserActionTokenInput)
@inject_password_reset_session()
async def password_verify(
    request: AppRequest,
    session: UserFlowSessionPasswordResetDTO,
    body: UserActionTokenInput,
) -> HTTPResponse:
    """Verify reset password by code.

    Requires a reset password session.
    """
    command = UserConfirmPasswordByCodeCommand(
        flow_session=session,
        token=body.token,
        ip_address=get_request_ip_address(request),
    )

    await use_cases.auth.reset_password.confirm_password_by_code(command)

    return empty()


@router.post("/auth/password/verify-link")
@openapi.tag("User Auth Reset Password")
@openapi.no_content()
@openapi.errors(InvalidUserActionTokenError)
@validator.body(UserActionTokenInput)
@load_password_reset_session()
async def password_verify_link(
    request: AppRequest,
    body: UserActionTokenInput,
) -> HTTPResponse:
    """Verify reset password by link.

    Does not require an authenticated session.
    """
    command = UserConfirmPasswordByLinkCommand(
        token=body.token,
        ip_address=get_request_ip_address(request),
        flow_session=request.ctx.flow_session,
    )

    result = await use_cases.auth.reset_password.confirm_password_by_link(command)

    response = empty()

    if result.created_flow_session:
        add_cookie(
            response,
            value=result.created_flow_session.session_key,
            cookie=config.context.user.get_flow_cookie_config_by_kind(
                result.created_flow_session.storage.kind,
            ),
            server_policy=request.app.ctx.server_cfg.cookie_policy,
            request_host=request.host,
        )

    return response
