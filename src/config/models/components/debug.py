from pydantic import BaseModel


class DebugConfig(BaseModel, frozen=True):
    expose_artifacts: bool = False
