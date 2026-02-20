from collections.abc import Callable
from typing import Any

from sqlalchemy import Alias, Column, Label, String, UnaryExpression, cast, func, text
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.orm import InstrumentedAttribute

ARG_COLUMN_TYPE = Column[Any] | Label[Any] | Alias | InstrumentedAttribute[Any]


def _object_builder_factory(
    build_method: Callable[[Any], Any],
    *args: ARG_COLUMN_TYPE,
) -> Any:
    parsed_args: list[Any] = []
    for arg in args:
        # TODO: AliasedClass, Alias using case?
        if isinstance(arg, Alias):
            # noinspection PyTypeChecker
            for c in arg.c:
                parsed_args.append(cast(c.name, String))
                parsed_args.append(c)
        else:
            parsed_args.append(cast(arg.name, String))
            parsed_args.append(arg)
    return build_method(*parsed_args)


def json_object_builder(*args: ARG_COLUMN_TYPE) -> Any:
    return _object_builder_factory(func.json_build_object, *args)


def jsonb_object_builder(*args: ARG_COLUMN_TYPE) -> Any:
    return _object_builder_factory(func.jsonb_build_object, *args)


def _array_builder_factory(
    *args: ARG_COLUMN_TYPE,
    order_by: list[UnaryExpression[Any]] | UnaryExpression[Any] | None,
    object_build_factory: Callable[[Any], Any],
    filters: Any = None,
) -> Any:
    build_agg = object_build_factory(*args)
    if order_by is not None:
        if isinstance(order_by, list):
            build_agg: Any = aggregate_order_by(build_agg, *order_by)  # type: ignore[no-redef]
        else:
            build_agg: Any = aggregate_order_by(build_agg, order_by)  # type: ignore[no-redef]
    json_agg: Any = func.jsonb_agg(build_agg)
    if filters is not None:
        json_agg: Any = json_agg.filter(filters)  # type: ignore[no-redef]
    return func.coalesce(json_agg, text("'[]'"))


def json_build_array_agg_builder(
    *args: ARG_COLUMN_TYPE,
    order_by: list[UnaryExpression[Any]] | UnaryExpression[Any] | None = None,
    filters: Any = None,
) -> Any:
    return _array_builder_factory(
        *args,
        order_by=order_by,
        object_build_factory=json_object_builder,
        filters=filters,
    )


def jsonb_build_array_agg_builder(
    *args: ARG_COLUMN_TYPE,
    order_by: list[UnaryExpression[Any]] | UnaryExpression[Any] | None = None,
    filters: Any = None,
) -> Any:
    return _array_builder_factory(
        *args,
        order_by=order_by,
        object_build_factory=jsonb_object_builder,
        filters=filters,
    )
