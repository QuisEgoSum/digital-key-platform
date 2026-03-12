from sanic import Blueprint, HTTPResponse

from context.user.application import queries
from context.user.application.dtos.entity.user import UserMeDTO
from infra import openapi
from infra.sanic.http.request import AppRequest
from infra.sanic.security.user_auth import AuthorizationSessionDTO, inject_user_session
from infra.sanic.utils.responses import json_response

router = Blueprint("UserMeRouter")


@router.get("/users/me")
@openapi.tag("User Me")
@openapi.response(UserMeDTO)
@inject_user_session()
async def get_user_me(
    _: AppRequest,
    session: AuthorizationSessionDTO,
) -> HTTPResponse:
    """Get user me."""
    return json_response(await queries.me.get_user_me(session.user_id))
