from collections.abc import AsyncGenerator

import pytest

from sanic_testing import TestManager

from entrypoint.user_http.main import create_app as create_user_http_app
from fixtures.sanic_types import AppSanicTestClient
from infra.sanic.types import AppSanic


@pytest.fixture()
def sanic_user_http_app() -> AppSanic:
    app = create_user_http_app()
    TestManager(app)
    return app


@pytest.fixture()
async def sanic_user_http_client(
    sanic_user_http_app: AppSanic,
) -> AsyncGenerator[AppSanicTestClient]:
    async with sanic_user_http_app.asgi_client as client:
        yield client
