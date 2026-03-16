import asyncio

from collections.abc import Coroutine
from typing import Any

from shared.utils.logger import get_logger

logger = get_logger(__name__)

BACKGROUND_TASKS: set[asyncio.Task[Any]] = set()


async def schedule_in_background(coroutine: Coroutine[Any, Any, Any]) -> None:
    await _schedule_in_background_asyncio(coroutine)


async def _schedule_in_background_asyncio(coroutine: Coroutine[Any, Any, Any]) -> None:
    task = asyncio.create_task(coroutine)
    BACKGROUND_TASKS.add(task)
    task.add_done_callback(BACKGROUND_TASKS.discard)
    task.add_done_callback(_log_task_result)


def _log_task_result(task: asyncio.Task[Any]) -> None:
    """Log unhandled exceptions from background tasks.

    Canceled tasks are ignored (cancellation is usually a normal shutdown path).
    """
    try:
        exc = task.exception()
    except asyncio.CancelledError:
        return
    except Exception:
        logger.exception("Failed to read background task exception")
        return

    if exc is None:
        return

    coro = task.get_coro()
    coro_name = getattr(coro, "__qualname__", None) or getattr(coro, "__name__", None)

    logger.exception(
        "Background task crashed",
        task_name=task.get_name(),
        coro=coro_name,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
