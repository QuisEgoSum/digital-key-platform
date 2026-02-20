from types import UnionType
from typing import Any, List, Union, get_args, get_origin  # noqa: UP035


def is_namedtuple_instance(obj: Any) -> bool:
    return (
        isinstance(obj, tuple) and hasattr(obj, "_asdict") and hasattr(obj, "_fields")
    )


def is_list_type(tp: Any) -> bool:
    origin = get_origin(tp)

    if origin in {list, List}:  # noqa: UP006
        return True

    if origin in (Union, UnionType):
        return any(is_list_type(arg) for arg in get_args(tp))

    return False
