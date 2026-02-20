from typing import TypeVar

from pydantic import BaseModel, ValidationError

from infra.sanic.validator.enums import TargetNameType
from infra.sanic.validator.types import RawPayload
from infra.sanic.validator.utils import pydantic_error_mapper
from infra.sanic.validator.validator_abc import ValidatorABC
from shared.utils.typing_utils import is_list_type

TP = TypeVar("TP", bound=RawPayload)
TR = TypeVar("TR", bound=BaseModel)


class ValidatorPydantic(ValidatorABC[TP, TR]):
    schema: type[TR]

    def get_query_list_fields(self) -> set[str]:
        if self.target_name != TargetNameType.QUERY:
            return set()
        list_fields = set()
        for field_name, field in self.schema.model_fields.items():
            outer_type = field.annotation
            if is_list_type(outer_type):
                list_fields.add(field_name)
        return list_fields

    def validate(self, payload: TP) -> TR:
        try:
            return self.schema.model_validate(payload)
        except ValidationError as ex:
            raise pydantic_error_mapper(ex, self.target_name) from ex

    def get_schema_fields(self) -> list[str]:
        return (
            list(self.schema.model_fields.keys())
            if self.target_name == TargetNameType.PARAMS
            else []
        )
