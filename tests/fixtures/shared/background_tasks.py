from collections.abc import Coroutine
from typing import Any

import pytest

from _pytest.monkeypatch import MonkeyPatch

from shared.utils import background_tasks


async def immediate_background(coroutine: Coroutine[Any, Any, Any]) -> None:
    await coroutine


@pytest.fixture(autouse=True)
def patch_background_tasks(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        background_tasks,
        "_schedule_in_background_asyncio",
        immediate_background,
    )
