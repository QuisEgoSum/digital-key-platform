import os

from typing import Any

from config import root_dir
from config.models.components.project import ProjectConfig
from infra import openapi
from shared.utils.logger import get_logger

logger = get_logger(__name__)


def setup_openapi(
    project: ProjectConfig,
    *,
    title: str | None = None,
) -> None:
    project_service_type: str = project.service

    openapi_spec = openapi.utils.get_raw_openapi()

    openapi_spec["info"]["title"] = title or (
        f"{format_project_name(project.name)} - "
        f"{format_service_name(project.service.value)}"
    )
    openapi_spec["info"]["version"] = project.version

    if "x-tagGroups" in openapi_spec:
        tags_dict: dict[str, dict[str, Any]] = {}

        for tag in openapi_spec["x-tagGroups"]:
            for name in tag["tags"]:
                tags_dict[name] = {"name": name, "description": ""}

        for tag_name in tags_dict:
            path = os.path.join(
                root_dir,
                "docs/openapi",
                project_service_type,
                tag_name + ".md",
            )
            if os.path.exists(path):
                logger.debug("Read tag description", tag_name=tag_name, path=path)
                with open(path) as file:
                    tags_dict[tag_name]["description"] = file.read()

        openapi_spec["tags"] = list(tags_dict.values())


def format_project_name(name: str) -> str:
    return name.replace("_", " ").title()


def format_service_name(service: str) -> str:
    return service.replace("_", " ").title().replace(" Api", " API")
