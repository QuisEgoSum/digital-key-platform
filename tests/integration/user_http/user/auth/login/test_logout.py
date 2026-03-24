from http import HTTPStatus

from fixtures.sanic_types import AppSanicTestClient
from fixtures.user.auth import UserAuthFactory
from fixtures.user.user import UserFactory
from fixtures.user.user_session import UserSessionQuery
from shared.errors.authorization import UnauthorizedError
from utils.cookie import parse_set_cookie_headers_by_name


async def test_logout_success(
    sanic_user_http_client: AppSanicTestClient,
    user_factory: UserFactory,
    user_auth_factory: UserAuthFactory,
    user_session_query: UserSessionQuery,
) -> None:
    created_user = await user_factory.create()
    auth_session = await user_auth_factory.create_auth_session(created_user.user.id)

    sanic_user_http_client.cookies["session"] = auth_session.session_key

    req, res = await sanic_user_http_client.post("/v1/auth/logout")

    assert res.status_code == HTTPStatus.NO_CONTENT
    assert req.ctx.session is not None

    cookies = parse_set_cookie_headers_by_name(res.headers.get_list("set-cookie"))

    assert len(cookies) == 1
    assert cookies["session"].is_deleted is True

    user_session = await user_session_query.get(auth_session.storage.session_id)

    assert user_session.is_deleted is True


async def test_logout_unauthorized(sanic_user_http_client: AppSanicTestClient) -> None:
    _, res = await sanic_user_http_client.post("/v1/auth/logout")

    assert res.status_code == HTTPStatus.UNAUTHORIZED
    assert res.json == UnauthorizedError().to_dict()
