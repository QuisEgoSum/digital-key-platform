import asyncio
import functools

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def limit_concurrency(semaphore: asyncio.Semaphore) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def limit_concurrency_by(limit: int) -> Callable[[F], F]:
    if limit < 0:
        raise ValueError("limit must be >= 0")

    semaphore = asyncio.Semaphore(limit)
    return limit_concurrency(semaphore)
