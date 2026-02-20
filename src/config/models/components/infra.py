from pydantic import BaseModel

from infra.persistence.config import PersistenceConfig


class InfraConfig(BaseModel):
    persistence: PersistenceConfig
