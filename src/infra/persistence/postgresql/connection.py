from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_tx_context import SQLAlchemyTransactionContext

from config import config

application_name = config.project.name + " - " + config.project.service.value


connect_args = {
    "server_settings": {"application_name": application_name},
}
psql_cfg = config.infra.persistence.databases.postgresql


engine = create_async_engine(
    psql_cfg.uri,
    connect_args=connect_args,
    pool_size=psql_cfg.pool_size,
    max_overflow=psql_cfg.max_overflow,
)

db = SQLAlchemyTransactionContext(engine)
