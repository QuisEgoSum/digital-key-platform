from infra.sanic.validator.enums import TargetNameType
from shared.errors.base import BadDataError, ValidationError


class SchemaValidationItemError(ValidationError):
    message: str
    code: int = 2
    location: list[str | int]

    def __init__(
        self,
        message: str,
        location: list[str | int],
    ) -> None:
        self.message = message
        self.location = location

        super().__init__()


class SchemaValidationError(ValidationError):
    message = "Validation errors"
    code: int = 1

    target: TargetNameType
    errors: list[SchemaValidationItemError]

    def __init__(
        self,
        target: TargetNameType,
        errors: list[SchemaValidationItemError],
    ) -> None:
        self.errors = errors
        self.target = target

        super().__init__()


class NotRequestProvidedError(BadDataError):
    message = "No request {target} provided"
    code = 3

    target: TargetNameType

    def __init__(self, target: TargetNameType):
        self.message = f"No request {target!s} provided"
        self.target = target

        super().__init__()
