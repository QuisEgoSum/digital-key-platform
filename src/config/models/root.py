from typing import Literal

from pydantic import BaseModel, Field

from config.models.components.context import BoundedContextConfig
from config.models.components.debug import DebugConfig
from config.models.components.entrypoint import EntrypointConfig
from config.models.components.infra import InfraConfig
from config.models.components.logger import LoggerConfig
from config.models.components.project import ProjectConfig
from config.models.components.regional import RegionalConfig
from config.models.components.security import SecurityConfig

type ConfigMode = Literal[
    "production",
    "development",
    "preproduction",
    "demo",
    "test",
    "local",
]


class AppConfig(BaseModel, frozen=True):
    project: ProjectConfig

    entrypoint: EntrypointConfig
    context: BoundedContextConfig = Field(default_factory=BoundedContextConfig)
    infra: InfraConfig

    logger: LoggerConfig = Field(default_factory=LoggerConfig)
    security: SecurityConfig

    regional: RegionalConfig

    debug: DebugConfig = Field(default_factory=DebugConfig)

    mode: ConfigMode
    root_dir: str = Field(..., description="Calculated automatically")

    @property
    def is_production(self) -> bool:
        return self.mode == "production"
