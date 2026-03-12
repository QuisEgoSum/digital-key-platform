import asyncio

from collections.abc import Coroutine
from typing import Any, TypeVar

from shared.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

BACKGROUND_TASKS: set[asyncio.Task[Any]] = set()


def _log_task_result(task: asyncio.Task[Any]) -> None:
    """Log unhandled exceptions from background tasks.

    Note: Cancelled tasks are ignored (cancellation is usually a normal shutdown path).
    """
    try:
        exc = task.exception()
    except asyncio.CancelledError:
        return
    except Exception:
        # In case task.exception() itself fails for some reason.
        logger.exception("Failed to read background task exception")
        return

    if exc is None:
        return

    task_name = getattr(task, "get_name", None)
    name = task.get_name() if callable(task_name) else None

    coro = getattr(task, "get_coro", lambda: None)()
    coro_name = getattr(coro, "__qualname__", None) or getattr(coro, "__name__", None)

    logger.exception(
        "Background task crashed",
        task_name=name,
        coro=coro_name,
        exc_info=(type(exc), exc, exc.__traceback__),
    )


def run_in_background[T](coroutine: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
    task = asyncio.create_task(coroutine)
    BACKGROUND_TASKS.add(task)
    task.add_done_callback(BACKGROUND_TASKS.discard)
    task.add_done_callback(_log_task_result)
    return task
