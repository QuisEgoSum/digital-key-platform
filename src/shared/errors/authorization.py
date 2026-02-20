from shared.errors.base import AuthenticationError


class UnauthorizedError(AuthenticationError):
    message = "Unauthorized"
    code = 10
