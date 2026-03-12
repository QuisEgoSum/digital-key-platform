from pydantic import BaseModel, SecretStr


class UserRegisterCommand(BaseModel, frozen=True):
    name: str
    email: str
    password: SecretStr
    timezone: str
    locale: str
    ip_address: str


class UserLoginCommand(BaseModel, frozen=True):
    email: str
    password: SecretStr
    ip_address: str
