from typing import TYPE_CHECKING
from urllib.parse import urljoin

from sanic import Blueprint, HTTPResponse, response
from sanic.response import JSONResponse

from infra import openapi
from infra.resources.redoc.loader import get_redoc_html
from infra.sanic.http.request import AppRequest
from infra.sanic.security.basic_auth import docs_auth
from shared.serialization.json import soft_json_dumps

if TYPE_CHECKING:
    from infra.sanic.types import AppSanic


router = Blueprint("Openapi")


@router.get("/docs")
@openapi.exclude()
@docs_auth()
async def get_docs(request: AppRequest) -> HTTPResponse:
    app: AppSanic = request.app

    return response.html(
        get_redoc_html(urljoin(app.ctx.server_config.base_path + "/", "openapi")),
        200,
    )


@router.get("/openapi")
@openapi.exclude()
@docs_auth()
async def get_spec(_: AppRequest) -> JSONResponse:
    return response.json(openapi.utils.get_raw_openapi(), dumps=soft_json_dumps)
