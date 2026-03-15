"""User Email error codes: 2010-2019."""

from shared.errors.base import BadDataError, ConflictError, NotFoundError


class UserEmailAlreadyExistsError(ConflictError):
    message = "User with email already exists."
    code = 2010


class UserEmailNotFoundError(NotFoundError):
    message = "User email not found."
    code = 2011


class UserEmailNotPrimaryError(BadDataError):
    message = "User email not primary."
    code = 2012
