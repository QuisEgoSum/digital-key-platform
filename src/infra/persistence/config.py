from pydantic import BaseModel

from infra.persistence.postgresql.config import PostgreSQLConfig
from infra.persistence.redis.config import RedisConfig


class DatabasesConfig(BaseModel):
    postgresql: PostgreSQLConfig
    redis: RedisConfig


class PersistenceConfig(BaseModel):
    databases: DatabasesConfig
