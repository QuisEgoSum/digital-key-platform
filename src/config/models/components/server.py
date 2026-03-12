from functools import cached_property
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from infra.http.cookie.config import CookiePolicyConfig


class ServerConfig(BaseModel, frozen=True):
    host: str = Field(min_length=1)
    port: int = Field(ge=1, le=65535)
    url: str
    trust_proxy_headers: bool

    cookie_policy: CookiePolicyConfig = Field(default_factory=CookiePolicyConfig)

    @cached_property
    def base_path(self) -> str:
        """Return the path component of the server URL.

        This usually represents the base path added by a reverse proxy
        (for example "/api" in "https://example.com/api").
        """
        return urlparse(self.url).path


class HTTPServerConfig(ServerConfig, frozen=True):
    workers: int = Field(ge=1, le=124)


class WSServerConfig(ServerConfig, frozen=True):
    pass
