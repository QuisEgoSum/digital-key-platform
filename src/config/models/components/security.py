from pydantic import BaseModel, SecretStr


class BasicAuthConfig(BaseModel, frozen=True):
    users: dict[str, SecretStr]


class SecurityDocsConfig(BaseModel, frozen=True):
    basic_auth: BasicAuthConfig


class TokensConfig(BaseModel, frozen=True):
    secret_key: str


class SecurityConfig(BaseModel, frozen=True):
    tokens: TokensConfig
    docs: SecurityDocsConfig
