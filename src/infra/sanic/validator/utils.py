from pydantic import ValidationError

from infra.sanic.validator.enums import TargetNameType
from infra.sanic.validator.errors import (
    SchemaValidationError,
    SchemaValidationItemError,
)


def pydantic_error_mapper(
    ex: ValidationError,
    target_name: TargetNameType,
    *,
    additional_loc_prefix: list[str | int] | None = None,
) -> SchemaValidationError:
    errors_list: list[SchemaValidationItemError] = []
    for error in ex.errors():
        loc = list(error["loc"])

        if additional_loc_prefix:
            loc = additional_loc_prefix + loc

        errors_list.append(
            SchemaValidationItemError(
                error["msg"],
                location=loc,
            ),
        )
    return SchemaValidationError(target_name, errors_list)
