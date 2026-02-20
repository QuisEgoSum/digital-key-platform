from typing import Literal

from pydantic import BaseModel


class LoggerConfig(BaseModel, frozen=True):
    level: Literal["INFO", "DEBUG", "ERROR", "WARNING"]
    format: Literal["plain", "json"]
