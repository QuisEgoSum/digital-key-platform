from collections.abc import Callable, Sequence
from typing import Any

from sqlalchemy import (
    JSON,
    Alias,
    ColumnElement,
    String,
    Subquery,
    cast,
    func,
    inspect,
    literal,
)
from sqlalchemy.dialects.postgresql import JSONB, aggregate_order_by
from sqlalchemy.orm import InstrumentedAttribute, MappedClassProtocol

type JsonKeyExprPair = tuple[str, Any]
type JsonObjectBuildArg = (
    InstrumentedAttribute[Any]
    | MappedClassProtocol[Any]
    | Alias
    | Subquery
    | JsonKeyExprPair
)
type OrderByArg = ColumnElement[Any] | Sequence[ColumnElement[Any]]


def _expand_argument(arg: Any) -> list[Any]:
    if isinstance(arg, tuple) and len(arg) == 2 and isinstance(arg[0], str):
        return [literal(arg[0], String()), arg[1]]

    columns = getattr(arg, "c", None)
    if columns is not None:
        result: list[Any] = []
        for c in columns:
            result.append(literal(c.key, String()))
            result.append(c)
        return result

    try:
        insp = inspect(arg)
    except Exception:
        insp = None

    if insp is not None and hasattr(insp, "mapper"):
        result = []
        for prop in insp.mapper.column_attrs:
            expr = getattr(arg, prop.key)
            result.append(literal(prop.key, String()))
            result.append(expr)
        return result

    if hasattr(arg, "name"):
        return [literal(arg.name, String()), arg]

    raise TypeError(f"Unsupported json builder argument: {arg!r}")


def _object_builder_factory(
    build_method: Callable[[Any], Any],
    *args: JsonObjectBuildArg,
) -> Any:
    parsed_args: list[Any] = []
    for arg in args:
        parsed_args.extend(_expand_argument(arg))
    return build_method(*parsed_args)


def json_object_builder(*args: JsonObjectBuildArg) -> Any:
    return _object_builder_factory(func.json_build_object, *args)


def jsonb_object_builder(*args: JsonObjectBuildArg) -> Any:
    return _object_builder_factory(func.jsonb_build_object, *args)


def _array_builder_factory(
    *args: JsonObjectBuildArg,
    order_by: OrderByArg | None,
    object_build_factory: Callable[[Any], Any],
    array_build_factory: Callable[[Any], Any],
    where: ColumnElement[bool] | None = None,
    default: Any,
) -> Any:
    build_agg = object_build_factory(*args)

    if order_by is not None:
        if isinstance(order_by, Sequence) and not isinstance(order_by, (str, bytes)):
            build_agg: Any = aggregate_order_by(build_agg, *order_by)  # type: ignore[no-redef]
        else:
            build_agg: Any = aggregate_order_by(build_agg, order_by)  # type: ignore[no-redef]

    json_agg: Any = array_build_factory(build_agg)

    if where is not None:
        json_agg: Any = json_agg.filter(where)  # type: ignore[no-redef]

    if default is not None:
        return func.coalesce(json_agg, default)
    return json_agg


def json_build_array_agg_builder(
    *args: JsonObjectBuildArg,
    order_by: OrderByArg | None = None,
    where: ColumnElement[bool] | None = None,
    empty_array_on_null: bool = True,
) -> Any:
    return _array_builder_factory(
        *args,
        order_by=order_by,
        object_build_factory=json_object_builder,
        array_build_factory=func.json_agg,
        where=where,
        default=cast(literal("[]"), JSON) if empty_array_on_null else None,
    )


def jsonb_build_array_agg_builder(
    *args: JsonObjectBuildArg,
    order_by: OrderByArg | None = None,
    where: ColumnElement[bool] | None = None,
    empty_array_on_null: bool = True,
) -> Any:
    return _array_builder_factory(
        *args,
        order_by=order_by,
        object_build_factory=jsonb_object_builder,
        array_build_factory=func.jsonb_agg,
        where=where,
        default=cast(literal("[]"), JSONB) if empty_array_on_null else None,
    )
