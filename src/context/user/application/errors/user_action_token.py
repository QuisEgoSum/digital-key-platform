"""User Auth error codes: 2030-2039."""

from typing import Literal

from context.user.application.dtos.entity.user_action_token import UserActionTokenDTO
from shared.errors.base import BadDataError

type InvalidUserActionTokenClassifier = Literal[
    "token_not_found",
    "token_expired",
    "token_mismatch",
    "flow_session_not_bound",
]


class InvalidUserActionTokenError(BadDataError):
    message = "Invalid user action token"
    code = 2030

    _classifier: InvalidUserActionTokenClassifier
    _action_token: UserActionTokenDTO | None

    def __init__(
        self,
        classifier: InvalidUserActionTokenClassifier,
        action_token: UserActionTokenDTO | None = None,
    ) -> None:
        self._classifier = classifier
        self._action_token = action_token

        super().__init__()

    @property
    def classifier(self) -> InvalidUserActionTokenClassifier:
        return self._classifier

    @property
    def action_token(self) -> UserActionTokenDTO | None:
        return self._action_token
