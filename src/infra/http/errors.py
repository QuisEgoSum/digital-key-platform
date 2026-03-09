from shared.errors.base import InternalError


class InternalServerError(InternalError):
    message = "Internal Server Error"
    code = 4
