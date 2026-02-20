from pydantic import BaseModel


class RedisConfig(BaseModel, frozen=True):
    host: str
    port: int
    password: str
    db: int = 0

    @property
    def uri(self) -> str:
        return f"redis://default:{self.password}@{self.host}:{self.port}/{self.db}"
