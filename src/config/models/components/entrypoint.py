from pydantic import BaseModel

from entrypoint.user_http.config import UserHTTPConfig


class EntrypointConfig(BaseModel):
    user_http: UserHTTPConfig
