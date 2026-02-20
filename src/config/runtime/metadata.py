import os
import tomllib

from typing import TypedDict, cast

root_dir: str = os.environ.get(
    "ROOT_DIR",
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../"),
    ),
)


class _Project(TypedDict):
    name: str
    version: str


class PyProject(TypedDict):
    project: _Project


with open(os.path.join(root_dir, "pyproject.toml"), encoding="utf-8") as file:
    project_metadata: PyProject = cast("PyProject", tomllib.loads(file.read()))
