from pydantic import BaseModel

from config.models.components.server import HTTPServerConfig


class UserHTTPConfig(BaseModel):
    server: HTTPServerConfig
