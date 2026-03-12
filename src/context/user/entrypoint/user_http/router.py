from sanic import Blueprint

from context.user.entrypoint.user_http.auth_handler import router as user_router
from context.user.entrypoint.user_http.me_handler import router as me_router

router = Blueprint.group(
    user_router,
    me_router,
    version=1,
)
