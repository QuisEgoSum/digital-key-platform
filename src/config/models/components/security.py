from pydantic import BaseModel, SecretStr


class BasicAuthConfig(BaseModel, frozen=True):
    users: dict[str, SecretStr]


class SecurityDocsConfig(BaseModel, frozen=True):
    basic_auth: BasicAuthConfig


class SecurityConfig(BaseModel, frozen=True):
    docs: SecurityDocsConfig
