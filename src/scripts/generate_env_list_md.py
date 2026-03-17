#!/usr/bin/env python

import enum

from pathlib import Path
from types import UnionType
from typing import Annotated, Any, Literal, Union, get_args, get_origin

from pydantic_core import PydanticUndefinedType
from tabulate import tabulate

from config.runtime.loader import get_config, manager


def format_type(tp: type) -> str:
    origin = get_origin(tp)
    args = get_args(tp)

    # Literal["a", "b"]
    if origin is Literal:
        return ", ".join(sorted(repr(a) for a in args))

    # Annotated[Literal["a", "b"], ...]
    if origin is Annotated:
        real_type = args[0]
        return format_type(real_type)

    # Optional[int] or Union[int, None] or X | Y
    if origin in (Union, UnionType):
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1 and len(args) == 2:
            return f"{format_type(non_none[0])}?"
        return ", ".join(sorted(format_type(a) for a in args))

    # Enum, IntEnum, StrEnum
    if isinstance(tp, type) and issubclass(tp, enum.Enum):
        return ", ".join(sorted(repr(member.value) for member in tp))

    # Built-in types: str, int, list, etc.
    if hasattr(tp, "__name__"):
        return tp.__name__

    return str(tp)


def format_default(val: Any) -> str:
    if val is ... or val is None or isinstance(val, PydanticUndefinedType):
        return "-"
    if isinstance(val, str):
        return f'"{val}"'
    return str(val)


def generate_env_list() -> None:
    config = get_config()
    output_path = Path(config.root_dir) / "docs/config/ENV_LIST.md"
    fields = manager.env_list

    table_data = []
    for f in fields:
        table_data.append(
            [
                f.name,
                format_type(f.type),
                (
                    format_default(f.default)
                    if f.name != "ROOT_DIR"
                    else "<calculated automatically>"
                ),
                f.description or "-",
            ],
        )

    headers = ["Environment variable", "Type", "Default", "Description"]
    markdown_table = tabulate(table_data, headers, tablefmt="github")

    Path(output_path).write_text(markdown_table, encoding="utf-8")


def run_generate_env_list() -> None:
    generate_env_list()


if __name__ == "__main__":
    run_generate_env_list()
