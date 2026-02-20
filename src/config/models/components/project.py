from pydantic import BaseModel, Field

from shared.enums.project import ProjectServiceType


class ProjectConfig(BaseModel, frozen=True):
    name: str = Field(
        ...,
        description="Calculated automatically from pyproject.toml",
    )
    version: str = Field(
        ...,
        description="Calculated automatically from pyproject.toml",
    )
    service: ProjectServiceType = Field(
        ...,
        description="The type of project service being launched",
    )
