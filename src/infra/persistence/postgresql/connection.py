__all__ = (
    "DBContext",
    "db",
    "engine",
)

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy_tx_context import SQLAlchemyTransactionContext

from config.runtime.loader import get_config

type DBContext = SQLAlchemyTransactionContext


def create_engine_from_config() -> AsyncEngine:
    config = get_config()
    psql_config = config.infra.persistence.databases.postgresql
    application_name = config.project.name + " - " + config.project.service.value

    return create_async_engine(
        psql_config.uri,
        connect_args={
            "server_settings": {
                "application_name": application_name,
            },
        },
        pool_size=psql_config.pool_size,
        max_overflow=psql_config.max_overflow,
    )


engine = create_engine_from_config()
db: DBContext = SQLAlchemyTransactionContext(engine)
