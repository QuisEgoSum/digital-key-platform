from sanic import Blueprint, HTTPResponse, empty

from config import config
from context.user.application import use_cases
from context.user.application.dtos.command.auth import (
    UserConfirmEmailByCodeCommand,
    UserConfirmEmailByLinkCommand,
    UserRequestConfirmEmailCommand,
)
from context.user.application.dtos.input.auth import (
    UserActionTokenInput,
)
from context.user.application.errors.user_action_token import (
    InvalidUserActionTokenError,
)
from context.user.application.errors.user_email import UserEmailNotFoundError
from infra import openapi
from infra.sanic import validator
from infra.sanic.http.request import AppRequest
from infra.sanic.security.user_auth import (
    UserEmailVerificationSessionDTO,
    inject_email_verification_session,
    load_email_verification_session,
)
from infra.sanic.utils.request import get_request_ip_address
from infra.sanic.utils.responses import add_cookie, delete_cookie

router = Blueprint("UserAuthEmailRouter")


@router.post("/auth/email/request-verification")
@openapi.tag("User Auth Confirm Email")
@openapi.errors(UserEmailNotFoundError)
@openapi.no_content()
@inject_email_verification_session()
async def request_confirm_email(
    request: AppRequest,
    session: UserEmailVerificationSessionDTO,
) -> HTTPResponse:
    """Request confirm email."""
    command = UserRequestConfirmEmailCommand(
        flow_session=session,
        ip_address=get_request_ip_address(request),
    )

    await use_cases.auth.confirm_email.request_confirm_email(command)

    return empty()


@router.post("/auth/email/verify")
@openapi.tag("User Auth Confirm Email")
@openapi.no_content()
@openapi.errors(InvalidUserActionTokenError, UserEmailNotFoundError)
@validator.body(UserActionTokenInput)
@inject_email_verification_session()
async def email_verify(
    request: AppRequest,
    session: UserEmailVerificationSessionDTO,
    body: UserActionTokenInput,
) -> HTTPResponse:
    """Verify user email by code.

    Requires an email verification session.

    On success the email verification session is invalidated.
    Depending on application configuration, an authorization session may be created automatically.
    """
    command = UserConfirmEmailByCodeCommand(
        flow_session=session,
        token=body.token,
        ip_address=get_request_ip_address(request),
    )

    result = await use_cases.auth.confirm_email.confirm_email_by_code(command)

    response = empty()

    delete_cookie(
        response,
        cookie=config.context.user.get_flow_cookie_config_by_kind(session.kind),
        server_policy=request.app.ctx.server_cfg.cookie_policy,
        request_host=request.host,
    )

    if result.auth_session:
        request.ctx.session = result.auth_session.storage

        add_cookie(
            response,
            value=result.auth_session.session_key,
            cookie=config.context.user.authorization.cookie,
            server_policy=request.app.ctx.server_cfg.cookie_policy,
            request_host=request.host,
        )

    return response


@router.post("/auth/email/verify-link")
@openapi.tag("User Auth Confirm Email")
@openapi.no_content()
@openapi.errors(InvalidUserActionTokenError, UserEmailNotFoundError)
@validator.body(UserActionTokenInput)
@load_email_verification_session()
async def email_verify_link(
    request: AppRequest,
    body: UserActionTokenInput,
) -> HTTPResponse:
    """Verify user email by link token.

    Does not require a flow session.

    On success the email is verified. If an email verification session exists, it is invalidated.
    Depending on application configuration, an authorization session may be created automatically.
    """
    command = UserConfirmEmailByLinkCommand(
        flow_session=request.ctx.flow_session,
        token=body.token,
        ip_address=get_request_ip_address(request),
    )

    result = await use_cases.auth.confirm_email.confirm_email_by_link(command)

    response = empty()

    if request.ctx.flow_session is not None:
        delete_cookie(
            response,
            cookie=config.context.user.get_flow_cookie_config_by_kind(
                request.ctx.flow_session.kind,
            ),
            server_policy=request.app.ctx.server_cfg.cookie_policy,
            request_host=request.host,
        )

    if result.auth_session is not None:
        request.ctx.session = result.auth_session.storage

        add_cookie(
            response,
            value=result.auth_session.session_key,
            cookie=config.context.user.authorization.cookie,
            server_policy=request.app.ctx.server_cfg.cookie_policy,
            request_host=request.host,
        )

    return response
