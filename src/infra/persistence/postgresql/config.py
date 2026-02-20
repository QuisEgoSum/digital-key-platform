from pydantic import BaseModel


class PostgreSQLConfig(BaseModel, frozen=True):
    username: str
    password: str
    db: str
    host: str
    port: int
    pool_size: int
    max_overflow: int

    @property
    def uri(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.db}"
