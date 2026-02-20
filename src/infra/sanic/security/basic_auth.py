from collections.abc import Callable
from typing import ParamSpec, TypeVar

from sanic import HTTPResponse

from config import config
from infra.sanic.security.base import basic_auth_factory

P = ParamSpec("P")
R = TypeVar("R")


def docs_auth() -> (
    Callable[[Callable[P, R | HTTPResponse]], Callable[P, R | HTTPResponse]]
):
    return basic_auth_factory(
        config.security.docs.basic_auth.users,
        realm="Access to the docs",
    )
