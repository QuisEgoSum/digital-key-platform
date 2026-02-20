from pydantic import BaseModel


class UserRegisterInputDTO(BaseModel):
    name: str
    email: str
    password: str
