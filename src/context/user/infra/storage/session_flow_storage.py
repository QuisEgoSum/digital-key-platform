import uuid

from datetime import timedelta
from typing import Any

import orjson

from context.user.application.enums.user_flow_session import UserFlowSessionKind
from infra.persistence.redis.connection import redis
from shared.serialization.json import strict_orjson_dumps
from shared.utils.logger import get_logger

logger = get_logger(__name__)

FLOW_SESSION_KIND_TO_REDIS_KEY_PREFIX: dict[UserFlowSessionKind, str] = {
    UserFlowSessionKind.PASSWORD_RESET: "user:session:password_reset",
    UserFlowSessionKind.EMAIL_VERIFICATION: "user:session:email_verification",
}


async def save_session(
    *,
    kind: UserFlowSessionKind,
    session_id: uuid.UUID,
    payload: dict[str, Any],
    ttl: timedelta,
) -> None:
    logger.debug(
        "Save user flow session data",
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
    kind: UserFlowSessionKind,
    session_id: uuid.UUID,
) -> dict[str, Any] | None:
    result: dict[str, Any] | None = None

    raw_data = await redis.get(_make_key(kind, session_id))

    if raw_data is not None:
        result = orjson.loads(raw_data)

    logger.debug(
        "Get user flow session data",
        session_id=session_id,
        kind=kind,
        payload=result,
    )

    return result


async def update_session_data(
    *,
    session_id: uuid.UUID,
    kind: UserFlowSessionKind,
    payload: dict[str, Any],
) -> None:
    logger.debug(
        "Update user flow session data",
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
    kind: UserFlowSessionKind,
    ttl: timedelta,
) -> None:
    logger.debug(
        "Update user flow session expire",
        session_id=session_id,
        kind=kind,
    )

    await redis.expire(
        _make_key(kind, session_id),
        ttl,
    )


async def delete_session(
    *,
    session_id: uuid.UUID,
    kind: UserFlowSessionKind,
) -> None:
    logger.debug(
        "Delete user flow session data",
        session_id=session_id,
        kind=kind,
    )

    await redis.delete(_make_key(kind, session_id))


def _make_key(kind: UserFlowSessionKind, session_id: uuid.UUID) -> str:
    if kind not in FLOW_SESSION_KIND_TO_REDIS_KEY_PREFIX:
        raise ValueError(f"Session kind {kind} not supported")

    return ":".join(
        [
            FLOW_SESSION_KIND_TO_REDIS_KEY_PREFIX[kind],
            str(session_id),
        ],
    )
