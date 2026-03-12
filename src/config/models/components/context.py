from pydantic import BaseModel, Field

from context.user.config.root import UserConfig


class BoundedContextConfig(BaseModel, frozen=True):
    user: UserConfig = Field(default_factory=UserConfig)
