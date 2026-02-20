import asyncio
import functools

from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from shared.utils.logger import get_logger

logger = get_logger(__name__)


F = TypeVar("F", bound=Callable[..., Any])
P = ParamSpec("P")
R = TypeVar("R")


def catch_and_log(
    default: Any = None,
) -> Callable[[Callable[P, Any]], Callable[P, Any]]:
    def decorator(func: Callable[P, Any]) -> Callable[P, Any]:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    logger.exception(
                        "Unhandled error in function",
                        function=func.__name__,
                    )
                    return default

        else:

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    logger.exception(
                        "Unhandled error in function",
                        function=func.__name__,
                    )
                    return default

        return wrapper

    return decorator
