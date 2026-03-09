from sanic import Blueprint, HTTPResponse

from context.user.public.dtos.entity.user import UserDTO
from context.user.public.dtos.input.user import UserRegisterInputDTO
from infra import openapi
from infra.sanic import validator
from infra.sanic.http.request import AppRequest
from infra.sanic.utils.responses import json_response

router = Blueprint("UserRouter")


@router.post("/auth/register")
@openapi.tag("User")
@openapi.response(UserDTO)
@validator.body(UserRegisterInputDTO)
async def user_register(_: AppRequest, body: UserRegisterInputDTO) -> HTTPResponse:
    """User registration."""

    return json_response(
        UserDTO(
            id=1,
            name=body.name,
            email=body.email,
        ),
    )
