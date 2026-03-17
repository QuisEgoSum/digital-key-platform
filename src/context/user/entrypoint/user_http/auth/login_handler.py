from typing import TYPE_CHECKING

from sanic import Blueprint, HTTPResponse, empty

from context.user.application import use_cases
from context.user.application.dtos.command.auth import (
    UserLoginCommand,
    UserLogoutCommand,
    UserRegisterCommand,
)
from context.user.application.dtos.input.auth import (
    UserLoginInput,
    UserRegisterInput,
)
from context.user.application.dtos.output.auth import (
    UserLoginEmailVerificationOutput,
    UserLoginLoggedInOutput,
    UserRegisterOutput,
)
from context.user.application.errors.auth import InvalidCredentialsError
from context.user.application.errors.user import (
    UserBannedError,
    UserTemporaryBlockedError,
)
from context.user.application.errors.user_email import UserEmailAlreadyExistsError
from infra import openapi
from infra.http.headers.accept_language import parse_accept_language
from infra.sanic import validator
from infra.sanic.http.request import AppRequest
from infra.sanic.security.user_auth import (
    UserAuthSessionDTO,
    inject_user_session,
)
from infra.sanic.utils.request import get_request_ip_address
from infra.sanic.utils.responses import add_cookie, delete_cookie, json_response
from shared.regional.i18n.locale import resolve_supported_locale
from shared.regional.timezone import resolve_timezone

if TYPE_CHECKING:
    from pydantic import BaseModel

    from config.models.root import AppConfig

router = Blueprint("UserAuthLoginRouter")


@router.post("/auth/register")
@openapi.tag("User Auth")
@openapi.errors(UserEmailAlreadyExistsError)
@openapi.response(UserRegisterOutput, status=201)
@validator.body(UserRegisterInput)
async def user_register(
    request: AppRequest,
    body: UserRegisterInput,
) -> HTTPResponse:
    """Register a new user."""
    config: AppConfig = request.app.ctx.config

    accept_locales = parse_accept_language(request.headers.get("Accept-Language"))

    locale = resolve_supported_locale(
        explicit_locale=body.locale,
        accept_locales=accept_locales,
        supported_locales=config.regional.i18n.supported_locales,
        default_locale=config.regional.i18n.default_locale,
    )
    timezone = resolve_timezone(
        explicit_timezone=body.timezone,
        default_timezone=config.regional.timezone.default_timezone,
    )

    command = UserRegisterCommand(
        name=body.name,
        email=body.email,
        password=body.password,
        locale=locale,
        timezone=timezone,
        ip_address=get_request_ip_address(request),
    )

    result = await use_cases.auth.register_user(command)

    # For access log.
    request.ctx.flow_session = result.flow_session.storage

    response: HTTPResponse = json_response(
        UserRegisterOutput(status=result.status, user=result.user),
        status=201,
    )

    add_cookie(
        response,
        value=result.flow_session.session_key,
        cookie=config.context.user.get_flow_cookie_config_by_kind(
            result.flow_session.storage.kind,
        ),
        server_policy=request.app.ctx.server_config.cookie_policy,
        request_host=request.host,
    )

    if result.auth_session:
        request.ctx.session = result.auth_session.storage
        add_cookie(
            response,
            value=result.auth_session.session_key,
            cookie=config.context.user.authorization.cookie,
            server_policy=request.app.ctx.server_config.cookie_policy,
            request_host=request.host,
        )

    return response


@router.post("/auth/login")
@openapi.tag("User Auth")
@openapi.responses(
    UserLoginLoggedInOutput,
    UserLoginEmailVerificationOutput,
)
@openapi.errors(
    InvalidCredentialsError,
    UserBannedError,
    UserTemporaryBlockedError,
)
@validator.body(UserLoginInput)
async def user_login(
    request: AppRequest,
    body: UserLoginInput,
) -> HTTPResponse:
    """Authenticate a user by email and password."""
    config: AppConfig = request.app.ctx.config

    command = UserLoginCommand(
        email=body.email,
        password=body.password,
        ip_address=get_request_ip_address(request),
    )

    result = await use_cases.auth.login(command)

    if result.status == "logged_in":
        response_payload: BaseModel = UserLoginLoggedInOutput(
            status="logged_in",
            user=result.user,
        )
    elif result.status == "email_verification_required":
        response_payload = UserLoginEmailVerificationOutput(
            status="email_verification_required",
        )
    else:
        raise ValueError(f"Unknown status {result.status}")

    response: HTTPResponse = json_response(response_payload)

    if result.auth_session is not None:
        request.ctx.session = result.auth_session.storage
        add_cookie(
            response,
            value=result.auth_session.session_key,
            cookie=config.context.user.authorization.cookie,
            server_policy=request.app.ctx.server_config.cookie_policy,
            request_host=request.host,
        )
    elif result.flow_session is not None:
        request.ctx.flow_session = result.flow_session.storage
        add_cookie(
            response,
            value=result.flow_session.session_key,
            cookie=config.context.user.get_flow_cookie_config_by_kind(
                result.flow_session.storage.kind,
            ),
            server_policy=request.app.ctx.server_config.cookie_policy,
            request_host=request.host,
        )

    return response


@router.post("/auth/logout")
@openapi.tag("User Auth")
@openapi.no_content()
@inject_user_session()
async def logout(request: AppRequest, session: UserAuthSessionDTO) -> HTTPResponse:
    """User logout."""
    config: AppConfig = request.app.ctx.config

    command = UserLogoutCommand(
        session=session,
        ip_address=get_request_ip_address(request),
    )

    await use_cases.auth.logout(command)

    response = empty()

    delete_cookie(
        response,
        cookie=config.context.user.authorization.cookie,
        server_policy=request.app.ctx.server_config.cookie_policy,
        request_host=request.host,
    )

    return response
