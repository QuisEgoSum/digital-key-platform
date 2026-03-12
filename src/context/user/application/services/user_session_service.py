import uuid

from dataclasses import asdict
from typing import Any, Literal, overload

from config import config
from context.user.application.dtos.entity.user_session import (
    UserSessionPasswordResetStateDTO,
    UserSessionStorageDTO,
)
from context.user.application.dtos.result.user_session import UserSessionCreateResult
from context.user.application.enums.user_session import UserSessionKind
from context.user.application.mapping.user_session import (
    map_storage_dict_to_storage_dto,
    map_user_session_to_storage_dto,
)
from context.user.infra.dao import user_session_dao
from context.user.infra.storage import session_storage
from shared.errors.authorization import UnauthorizedError
from shared.security.hash import compute_scoped_hmac
from shared.security.tokens import generate_urlsafe_token


@overload
async def create_session(
    user_id: int,
    kind: Literal[UserSessionKind.AUTHORIZATION, UserSessionKind.EMAIL_VERIFICATION],
    ip_address: str,
) -> UserSessionCreateResult[None]: ...


@overload
async def create_session(
    user_id: int,
    kind: Literal[UserSessionKind.PASSWORD_RESET],
    ip_address: str,
) -> UserSessionCreateResult[UserSessionPasswordResetStateDTO]: ...


async def create_session(
    user_id: int,
    kind: UserSessionKind,
    ip_address: str,
) -> UserSessionCreateResult[Any]:
    cfg = config.context.user.get_session_config_by_kind(kind)

    if cfg.active_session_limit != 0:
        sessions = await user_session_dao.soft_delete_user_sessions_exceeding_limit(
            user_id=user_id,
            kind=kind,
            limit=cfg.active_session_limit,
        )

        for session in sessions:
            await session_storage.delete_session(
                session_id=session.id,
                kind=kind,
            )

    session = await user_session_dao.insert_session(
        user_id=user_id,
        kind=kind,
        created_ip=ip_address,
    )

    secret = generate_urlsafe_token()
    secret_hash = compute_scoped_hmac(
        value=secret,
        secret=config.security.tokens.secret_key,
        scope=kind.value,
    )

    storage_data = map_user_session_to_storage_dto(session, secret_hash)

    await session_storage.save_session(
        kind=kind,
        session_id=session.id,
        payload=asdict(storage_data),
        ttl=cfg.expires_interval,
    )

    return UserSessionCreateResult(
        session_key=f"{session.id!s}:{secret}",
        storage=storage_data,
    )


@overload
async def verify_session(
    session_id: uuid.UUID,
    secret: str,
    kind: Literal[UserSessionKind.AUTHORIZATION, UserSessionKind.EMAIL_VERIFICATION],
) -> UserSessionStorageDTO[None]: ...


@overload
async def verify_session(
    session_id: uuid.UUID,
    secret: str,
    kind: Literal[UserSessionKind.PASSWORD_RESET],
) -> UserSessionStorageDTO[UserSessionPasswordResetStateDTO]: ...


@overload
async def verify_session(
    session_id: uuid.UUID,
    secret: str,
    kind: UserSessionKind,
) -> UserSessionStorageDTO[Any]: ...


async def verify_session(
    session_id: uuid.UUID,
    secret: str,
    kind: UserSessionKind,
) -> UserSessionStorageDTO[Any]:
    raw_data = await session_storage.get_session_data(
        session_id=session_id,
        kind=kind,
    )

    if raw_data is None:
        raise UnauthorizedError()

    cfg = config.context.user.get_session_config_by_kind(kind)

    storage_data = map_storage_dict_to_storage_dto(raw_data)

    secret_hash = compute_scoped_hmac(
        value=secret,
        secret=config.security.tokens.secret_key,
        scope=kind.value,
    )

    if storage_data.secret_hash != secret_hash:
        raise UnauthorizedError()

    if cfg.auto_renewal:
        await session_storage.update_session_expire(
            session_id=session_id,
            kind=kind,
            ttl=cfg.expires_interval,
        )

    return storage_data


async def update_session_data(
    *,
    session_id: uuid.UUID,
    kind: UserSessionKind,
    storage_data: UserSessionStorageDTO[Any],
) -> None:
    await session_storage.update_session_data(
        session_id=session_id,
        kind=kind,
        payload=asdict(storage_data),
    )


async def delete_session(
    *,
    session_id: uuid.UUID,
    kind: UserSessionKind,
) -> None:
    await user_session_dao.soft_delete_session_by_id(session_id)
    await session_storage.delete_session(
        kind=kind,
        session_id=session_id,
    )


async def delete_user_sessions(
    user_id: int,
    kind: UserSessionKind,
    exclude_id: uuid.UUID | None = None,
) -> None:
    sessions = await user_session_dao.soft_delete_user_sessions(
        user_id=user_id,
        kind=kind,
        exclude_id=exclude_id,
    )
    for session in sessions:
        await session_storage.delete_session(
            session_id=session.id,
            kind=kind,
        )
