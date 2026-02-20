from sanic import Request

from infra.sanic.ctx import AppSanicRequestCTX
from infra.sanic.types import AppSanic


class AppRequest(Request[AppSanic, AppSanicRequestCTX]):
    # https://sanic.dev/en/guide/basics/request.html#custom-request-context
    @staticmethod
    def make_context() -> AppSanicRequestCTX:
        return AppSanicRequestCTX()
