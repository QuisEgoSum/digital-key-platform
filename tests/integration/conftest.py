import os
import uuid

from collections.abc import AsyncGenerator, Generator

import asyncpg
import psycopg
import pytest

from _pytest.monkeypatch import MonkeyPatch
from alembic import command
from alembic.config import Config
from asyncpg import Connection
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_tx_context import SQLAlchemyTransactionContext

from config import config
from infra.persistence.postgresql import connection as psql_connection
from infra.persistence.redis.connection import redis


@pytest.fixture(scope="session", autouse=True)
def prepare_template_db() -> Generator[None]:
    """Create template database for tests and apply migrations.

    The database is created once per test session and migrated to the latest
    schema version. Each test then creates its own database using
    `CREATE DATABASE ... TEMPLATE ...`, which is significantly faster than
    running migrations for every test.
    """
    psql_c = config.infra.persistence.databases.postgresql

    main_psql_uri = f"postgresql://{psql_c.username}:{psql_c.password}@{psql_c.host}:{psql_c.port}/postgres"
    template_psql_uri = f"postgresql://{psql_c.username}:{psql_c.password}@{psql_c.host}:{psql_c.port}/{psql_c.db}"

    with psycopg.connect(main_psql_uri, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(f'DROP DATABASE IF EXISTS "{psql_c.db}" WITH (FORCE)')
        cur.execute(f'CREATE DATABASE "{psql_c.db}"')

    cfg = Config()

    migrations_path = os.path.join(os.path.dirname(__file__), "../../migrations")

    cfg.set_main_option("sqlalchemy.url", template_psql_uri)
    cfg.set_main_option("script_location", migrations_path)

    command.upgrade(cfg, "head")

    yield

    with psycopg.connect(main_psql_uri, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(f'DROP DATABASE IF EXISTS "{psql_c.db}" WITH (FORCE)')


@pytest.fixture(autouse=True)
async def db_context(
    monkeypatch: MonkeyPatch,
) -> AsyncGenerator[SQLAlchemyTransactionContext]:
    """Create an isolated database for a single test.

    A new database is created using the prepared template database and a new
    SQLAlchemy engine is initialized for it. The application's global database
    connection (`postgresql.connection.db`) is monkeypatched to use this engine.

    After the test finishes, the engine is disposed and the database is dropped.
    """
    psql_c = config.infra.persistence.databases.postgresql

    test_db = f"{psql_c.db}_{uuid.uuid4().hex[:8]}"

    main_psql_uri = f"postgresql://{psql_c.username}:{psql_c.password}@{psql_c.host}:{psql_c.port}/postgres"
    test_db_uri = f"postgresql+asyncpg://{psql_c.username}:{psql_c.password}@{psql_c.host}:{psql_c.port}/{test_db}"

    conn: Connection = await asyncpg.connect(main_psql_uri)

    await conn.execute(f'CREATE DATABASE "{test_db}" TEMPLATE "{psql_c.db}"')

    connect_args = {
        "max_cached_statement_lifetime": 0,
        "statement_cache_size": 0,
        "server_settings": {"application_name": "test"},
    }
    engine = create_async_engine(
        test_db_uri,
        connect_args=connect_args,
        pool_size=10,
        max_overflow=40,
        pool_pre_ping=True,
    )
    db = SQLAlchemyTransactionContext(engine)

    monkeypatch.setattr(
        psql_connection.db,
        "_engine",
        db._engine,
    )
    monkeypatch.setattr(
        psql_connection.db,
        "_default_session_maker",
        db._default_session_maker,
    )
    monkeypatch.setattr(
        psql_connection.db,
        "_session_var",
        db._session_var,
    )

    try:
        yield db
    finally:
        await engine.dispose()
        await conn.execute(f'DROP DATABASE IF EXISTS "{test_db}" WITH (FORCE)')
        await conn.close()


@pytest.fixture(autouse=True)
async def redis_client() -> AsyncGenerator[Redis]:  # type: ignore[type-arg]
    """Reset Redis state between tests and close connections.

    Redis client keeps references to the asyncio event loop. Without explicit
    disconnection after a test, the next test may attempt to reuse connections
    bound to a closed loop, causing runtime errors.
    """
    await redis.flushdb()

    try:
        yield redis
    finally:
        await redis.connection_pool.disconnect()
