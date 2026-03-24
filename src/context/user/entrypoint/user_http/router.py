from sanic import Blueprint

from context.user.entrypoint.user_http.auth.email_handler import (
    router as auth_email_router,
)
from context.user.entrypoint.user_http.auth.login_handler import (
    router as auth_login_router,
)
from context.user.entrypoint.user_http.auth.reset_password import (
    router as auth_password_router,
)
from context.user.entrypoint.user_http.me_handler import router as me_router

router = Blueprint.group(
    auth_login_router,
    auth_email_router,
    auth_password_router,
    me_router,
    version=1,
)
