from collections.abc import Callable
from typing import Any

import pytest

from sqlalchemy import Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, aliased, mapped_column

from infra.persistence.postgresql.funcs import (
    json_build_array_agg_builder,
    json_object_builder,
    jsonb_build_array_agg_builder,
    jsonb_object_builder,
)


class Base(DeclarativeBase):
    __abstract__ = True


class SaTestModel(Base):
    __tablename__ = "test_model"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    field_1: Mapped[int] = mapped_column(Integer(), nullable=False)
    field_2: Mapped[str] = mapped_column(String(), nullable=False)


@pytest.mark.parametrize(
    "method, sql_method",
    [
        (json_object_builder, "json_build_object"),
        (jsonb_object_builder, "jsonb_build_object"),
    ],
)
def test_json_object_builder_method_type(
    method: Callable[..., Any],
    sql_method: str,
) -> None:
    stmt = method(SaTestModel)

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        f"{sql_method}('id', test_model.id, 'field_1', "
        "test_model.field_1, 'field_2', test_model.field_2)"
    )


def test_json_object_builder_model() -> None:
    stmt = json_object_builder(SaTestModel)

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        "json_build_object('id', test_model.id, 'field_1', "
        "test_model.field_1, 'field_2', test_model.field_2)"
    )


def test_json_object_builder_fields() -> None:
    stmt = json_object_builder(
        SaTestModel.id,
        SaTestModel.field_1.label("test_field_1"),
    )

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        "json_build_object('id', test_model.id, 'test_field_1', test_model.field_1)"
    )


def test_json_object_builder_aliased() -> None:
    a = aliased(SaTestModel, name="a")

    stmt = json_object_builder(a)

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        "json_build_object('id', a.id, 'field_1', a.field_1, 'field_2', a.field_2)"
    )


def test_json_object_builder_aliased_fields() -> None:
    a = aliased(SaTestModel, name="a")

    stmt = json_object_builder(a.id, a.field_1.label("test_field_1"))

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == ("json_build_object('id', a.id, 'test_field_1', a.field_1)")


def test_json_object_builder_subquery_alias() -> None:
    sq = select(
        SaTestModel.id,
        SaTestModel.field_1.label("test_field_1"),
        SaTestModel.field_2,
    ).alias("sq")

    stmt = json_object_builder(sq)

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        "json_build_object('id', sq.id, 'test_field_1', sq.test_field_1, 'field_2', sq.field_2)"
    )


def test_json_object_builder_subquery_alias_fields() -> None:
    sq = select(
        SaTestModel.id,
        SaTestModel.field_1.label("test_field_1"),
        SaTestModel.field_2,
    ).alias("sq")

    stmt = json_object_builder(
        sq.c.id,
        sq.c.test_field_1,
        sq.c.field_2.label("test_field_2"),
    )

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        "json_build_object('id', sq.id, 'test_field_1', sq.test_field_1, 'test_field_2', sq.field_2)"
    )


def test_json_object_builder_expr_pair() -> None:
    stmt = json_object_builder(("test_id", SaTestModel.id), SaTestModel.field_1)

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        "json_build_object('test_id', test_model.id, 'field_1', test_model.field_1)"
    )


@pytest.mark.parametrize(
    "method, sql_method, sql_agg_method, sql_cast_type",
    [
        (json_build_array_agg_builder, "json_build_object", "json_agg", "JSON"),
        (jsonb_build_array_agg_builder, "jsonb_build_object", "jsonb_agg", "JSONB"),
    ],
)
def test_json_build_array_agg_builder_method_type(
    method: Callable[..., Any],
    sql_method: str,
    sql_agg_method: str,
    sql_cast_type: str,
) -> None:
    stmt = method(SaTestModel)

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        f"coalesce({sql_agg_method}({sql_method}('id', test_model.id, 'field_1', test_model.field_1, 'field_2', "
        f"test_model.field_2)), CAST('[]' AS {sql_cast_type}))"
    )


def test_json_build_array_agg_builder_where() -> None:
    stmt = json_build_array_agg_builder(SaTestModel, where=SaTestModel.id > 10)

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        "coalesce(json_agg(json_build_object('id', test_model.id, 'field_1', test_model.field_1, 'field_2', "
        "test_model.field_2)) FILTER (WHERE test_model.id > 10), CAST('[]' AS JSON))"
    )


def test_json_build_array_agg_builder_where_order_by() -> None:
    stmt = json_build_array_agg_builder(SaTestModel, order_by=SaTestModel.id.desc())

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        "coalesce(json_agg(json_build_object('id', test_model.id, 'field_1', test_model.field_1, 'field_2', "
        "test_model.field_2) ORDER BY test_model.id DESC), CAST('[]' AS JSON))"
    )


def test_json_build_array_agg_builder_where_order_by_list() -> None:
    stmt = json_build_array_agg_builder(
        SaTestModel,
        order_by=[SaTestModel.id.desc(), SaTestModel.field_1.asc()],
    )

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        "coalesce(json_agg(json_build_object('id', test_model.id, 'field_1', test_model.field_1, 'field_2', "
        "test_model.field_2) ORDER BY test_model.id DESC, test_model.field_1 ASC), CAST('[]' AS JSON))"
    )


def test_json_build_array_agg_builder_without_default() -> None:
    stmt = json_build_array_agg_builder(SaTestModel, empty_array_on_null=False)

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        "json_agg(json_build_object('id', test_model.id, 'field_1', test_model.field_1, 'field_2', test_model.field_2))"
    )


def test_json_build_array_agg_builder_combined() -> None:
    stmt = json_build_array_agg_builder(
        SaTestModel,
        where=SaTestModel.id > 10,
        order_by=[SaTestModel.id.desc(), SaTestModel.field_1.asc()],
    )

    sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert sql == (
        "coalesce(json_agg(json_build_object('id', test_model.id, 'field_1', test_model.field_1, 'field_2', "
        "test_model.field_2) ORDER BY test_model.id DESC, test_model.field_1 ASC) "
        "FILTER (WHERE test_model.id > 10), CAST('[]' AS JSON))"
    )
