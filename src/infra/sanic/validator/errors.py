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
    target: str
    code: int = 1
    message = "Validation errors"
    errors: list[SchemaValidationItemError]

    def __init__(
        self,
        target: TargetNameType | str,
        errors: list[SchemaValidationItemError],
    ) -> None:
        super().__init__()
        self.errors = errors
        self.target = (
            str(target.value) if isinstance(target, TargetNameType) else target
        )


class NotRequestProvidedError(BadDataError):
    code = 3
    target: str

    def __init__(self, target: TargetNameType):
        super().__init__()
        self.message = f"No request {target.value} provided"
        self.target = str(target.value)
