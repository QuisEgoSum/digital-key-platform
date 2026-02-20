from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def chunk_array[T](data: Sequence[T], chunk_size: int) -> list[Sequence[T]]:
    if chunk_size < 0:
        raise ValueError("chunk_size must be >= 0")
    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]
