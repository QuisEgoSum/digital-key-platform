"""User Email error codes: 2010-2019."""

from context.user.application.dtos.entity.user_email import UserEmailDTO
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


class UserEmailAlreadyVerifiedError(ConflictError):
    message = "User email already verified."
    code = 2013

    _user_email: UserEmailDTO

    def __init__(self, user_email: UserEmailDTO) -> None:
        self._user_email = user_email

        super().__init__()

    @property
    def user_email(self) -> UserEmailDTO:
        return self._user_email
