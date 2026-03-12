"""User Email error codes: 2010-2019."""

from shared.errors.base import ConflictError


class UserEmailAlreadyExistsError(ConflictError):
    message = "User with email already exists."
    code = 2010
