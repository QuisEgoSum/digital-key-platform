from typing import Any, TypeVar

from pydantic import BaseModel

from infra.sanic.validator.enums import TargetNameType
from infra.sanic.validator.types import RawPayload
from infra.sanic.validator.validator_abc import ValidatorABC
from infra.sanic.validator.validator_pydantic import ValidatorPydantic

TP = TypeVar("TP", bound=BaseModel)


def validator_factory[TP](
    *,
    schema: type[TP],
    target: TargetNameType,
    pass_data: bool = True,
    docs: bool = True,
) -> ValidatorABC[RawPayload, Any]:
    if issubclass(schema, BaseModel):
        return ValidatorPydantic(schema, target, pass_data=pass_data, docs=docs)
    else:
        raise NotImplementedError()


def body[TP](
    schema: type[TP],
    *,
    pass_data: bool = True,
    docs: bool = True,
) -> ValidatorABC[RawPayload, Any]:
    return validator_factory(
        schema=schema,
        target=TargetNameType.BODY,
        pass_data=pass_data,
        docs=docs,
    )


def query[TP](
    schema: type[TP],
    *,
    pass_data: bool = True,
    docs: bool = True,
) -> ValidatorABC[RawPayload, Any]:
    return validator_factory(
        schema=schema,
        target=TargetNameType.QUERY,
        pass_data=pass_data,
        docs=docs,
    )


def params[TP](
    schema: type[TP],
    *,
    pass_data: bool = True,
    docs: bool = True,
) -> ValidatorABC[RawPayload, Any]:
    return validator_factory(
        schema=schema,
        target=TargetNameType.PARAMS,
        pass_data=pass_data,
        docs=docs,
    )


def headers[TP](
    schema: type[TP],
    *,
    pass_data: bool = True,
    docs: bool = True,
) -> ValidatorABC[RawPayload, Any]:
    return validator_factory(
        schema=schema,
        target=TargetNameType.HEADERS,
        pass_data=pass_data,
        docs=docs,
    )


def validate[TP](
    schema: type[TP],
    *,
    target: TargetNameType = TargetNameType.UNION,
    payload: RawPayload,
    pass_data: bool = True,
) -> TP:
    return validator_factory(
        schema=schema,
        target=target,
        pass_data=pass_data,
    ).validate(payload)
