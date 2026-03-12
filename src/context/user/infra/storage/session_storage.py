import uuid

from datetime import timedelta
from typing import Any

import orjson

from context.user.application.enums.user_session import UserSessionKind
from infra.persistence.redis.connection import redis
from shared.serialization.json import strict_orjson_dumps
from shared.utils.logger import get_logger

logger = get_logger(__name__)

SESSION_KIND_TO_REDIS_KEY_PREFIX: dict[UserSessionKind, str] = {
    UserSessionKind.AUTHORIZATION: "user:session:auth",
    UserSessionKind.PASSWORD_RESET: "user:session:password_reset",
    UserSessionKind.EMAIL_VERIFICATION: "user:session:email_verification",
}


async def save_session(
    *,
    kind: UserSessionKind,
    session_id: uuid.UUID,
    payload: dict[str, Any],
    ttl: timedelta,
) -> None:
    logger.debug(
        "Save user session data",
        session_id=session_id,
        kind=kind,
        payload=payload,
    )

    await redis.set(
        _make_key(kind, session_id),
        strict_orjson_dumps(payload),
        ex=ttl,
    )


async def get_session_data(
    *,
    kind: UserSessionKind,
    session_id: uuid.UUID,
) -> dict[str, Any] | None:
    result: dict[str, Any] | None = None

    raw_data = await redis.get(_make_key(kind, session_id))

    if raw_data is not None:
        result = orjson.loads(raw_data)

    logger.debug(
        "Get user session data",
        session_id=session_id,
        kind=kind,
        payload=result,
    )

    return result


async def update_session_data(
    *,
    session_id: uuid.UUID,
    kind: UserSessionKind,
    payload: dict[str, Any],
) -> None:
    logger.debug(
        "Update user session data",
        session_id=session_id,
        kind=kind,
        payload=payload,
    )

    await redis.set(
        _make_key(kind, session_id),
        strict_orjson_dumps(payload),
        keepttl=True,
    )


async def update_session_expire(
    *,
    session_id: uuid.UUID,
    kind: UserSessionKind,
    ttl: timedelta,
) -> None:
    logger.debug(
        "Update user session expire",
        session_id=session_id,
        kind=kind,
    )

    await redis.expire(
        _make_key(kind, session_id),
        ttl,
    )


async def delete_session(
    *,
    kind: UserSessionKind,
    session_id: uuid.UUID,
) -> None:
    logger.debug(
        "Delete user session data",
        session_id=session_id,
        kind=kind,
    )

    await redis.delete(_make_key(kind, session_id))


def _make_key(session_kind: UserSessionKind, session_id: uuid.UUID) -> str:
    if session_kind not in SESSION_KIND_TO_REDIS_KEY_PREFIX:
        raise ValueError(f"Session kind {session_kind} not supported")

    return ":".join(
        [
            SESSION_KIND_TO_REDIS_KEY_PREFIX[session_kind],
            str(session_id),
        ],
    )
