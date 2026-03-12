"""User Auth error codes: 2020-2029."""

from typing import Literal

from shared.errors.base import AuthenticationError

type InvalidCredentialsClassifier = Literal[
    "user_not_found",
    "invalid_password",
    "unset_password",
    "user_deleted",
]


class InvalidCredentialsError(AuthenticationError):
    message = "Invalid credentials"
    code = 2020

    _classifier: InvalidCredentialsClassifier

    def __init__(self, classifier: InvalidCredentialsClassifier) -> None:
        self._classifier = classifier
        super().__init__()

    @property
    def classifier(self) -> InvalidCredentialsClassifier:
        return self._classifier
