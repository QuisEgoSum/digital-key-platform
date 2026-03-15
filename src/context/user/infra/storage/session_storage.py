import uuid

from datetime import timedelta
from typing import Any, Final

import orjson

from infra.persistence.redis.connection import redis
from shared.serialization.json import strict_orjson_dumps
from shared.utils.logger import get_logger

logger = get_logger(__name__)

USER_SESSION_REDIS_PREFIX: Final[str] = "user:session:auth"


async def save_session(
    *,
    session_id: uuid.UUID,
    payload: dict[str, Any],
    ttl: timedelta,
) -> None:
    logger.debug(
        "Save user session data",
        session_id=session_id,
        payload=payload,
    )

    await redis.set(
        _make_key(session_id),
        strict_orjson_dumps(payload),
        ex=ttl,
    )


async def get_session_data(
    *,
    session_id: uuid.UUID,
) -> dict[str, Any] | None:
    result: dict[str, Any] | None = None

    raw_data = await redis.get(_make_key(session_id))

    if raw_data is not None:
        result = orjson.loads(raw_data)

    logger.debug(
        "Get user session data",
        session_id=session_id,
        payload=result,
    )

    return result


async def update_session_data(
    *,
    session_id: uuid.UUID,
    payload: dict[str, Any],
) -> None:
    logger.debug(
        "Update user session data",
        session_id=session_id,
        payload=payload,
    )

    await redis.set(
        _make_key(session_id),
        strict_orjson_dumps(payload),
        keepttl=True,
    )


async def update_session_expire(
    *,
    session_id: uuid.UUID,
    ttl: timedelta,
) -> None:
    logger.debug(
        "Update user session expire",
        session_id=session_id,
    )

    await redis.expire(
        _make_key(session_id),
        ttl,
    )


async def delete_session(
    *,
    session_id: uuid.UUID,
) -> None:
    logger.debug(
        "Delete user session data",
        session_id=session_id,
    )

    await redis.delete(_make_key(session_id))


def _make_key(session_id: uuid.UUID) -> str:
    return ":".join(
        [
            USER_SESSION_REDIS_PREFIX,
            str(session_id),
        ],
    )
