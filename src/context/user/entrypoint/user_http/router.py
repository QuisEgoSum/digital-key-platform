from sanic import Blueprint

from context.user.entrypoint.user_http.auth_handler import router as user_router

router = Blueprint.group(
    user_router,
    version=1,
)
