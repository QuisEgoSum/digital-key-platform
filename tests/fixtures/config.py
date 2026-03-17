from dataclasses import dataclass
from typing import Any

import pytest

from _pytest.monkeypatch import MonkeyPatch
from pydantic import BaseModel

from config.runtime import loader


@dataclass()
class AppConfigPatch:
    monkeypatch: MonkeyPatch

    def replace_config(
        self,
        updates: dict[tuple[str, ...], Any],
    ) -> None:
        test_config = self._replace_config(
            loader.get_config(),
            updates,
        )
        self.monkeypatch.setattr(loader, "_config", test_config)

    @classmethod
    def _replace_config(
        cls,
        config: BaseModel,
        updates: dict[tuple[str, ...], Any],
    ) -> BaseModel:
        result = config

        for path, value in updates.items():
            result = cls._apply_path(result, path, value)

        return result

    @classmethod
    def _apply_path(
        cls,
        model: BaseModel,
        path: tuple[str, ...],
        value: Any,
    ) -> BaseModel:
        field = path[0]

        if len(path) == 1:
            return model.model_copy(update={field: value})

        nested = getattr(model, field)
        updated_nested = cls._apply_path(nested, path[1:], value)

        return model.model_copy(update={field: updated_nested})


@pytest.fixture()
def app_config_patch(monkeypatch: MonkeyPatch) -> AppConfigPatch:
    return AppConfigPatch(monkeypatch)
