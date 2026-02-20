from typing import Literal

from pydantic import BaseModel, Field

from config.models.components.entrypoint import EntrypointConfig
from config.models.components.infra import InfraConfig
from config.models.components.logger import LoggerConfig
from config.models.components.project import ProjectConfig
from config.models.components.security import SecurityConfig
from config.runtime.metadata import root_dir


class Config(BaseModel, frozen=True):
    project: ProjectConfig

    entrypoint: EntrypointConfig
    infra: InfraConfig

    logger: LoggerConfig
    security: SecurityConfig

    mode: Literal[
        "production",
        "development",
        "preproduction",
        "demo",
        "test",
        "local",
    ]
    root_dir: str = Field(root_dir, description="Calculated automatically")

    @property
    def is_production(self) -> bool:
        return self.mode == "production"
