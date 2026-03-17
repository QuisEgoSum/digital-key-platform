import uuid

from dataclasses import asdict

from config.runtime.loader import get_config
from context.user.application.dtos.entity.user_session import (
    UserSessionStorageDTO,
)
from context.user.application.dtos.result.user_session import UserSessionCreateResult
from context.user.application.mapping.user_session import (
    map_storage_dict_to_storage_dto,
    map_user_session_to_storage_dto,
)
from context.user.infra.dao import user_session_dao
from context.user.infra.storage import session_storage
from shared.errors.authorization import UnauthorizedError
from shared.security.hash import compute_scoped_hmac
from shared.security.tokens import generate_urlsafe_token


async def create_session(
    user_id: int,
    ip_address: str | None,
) -> UserSessionCreateResult:
    config = get_config()
    auth_config = config.context.user.authorization.session

    if auth_config.active_session_limit != 0:
        sessions = await user_session_dao.soft_delete_user_sessions_exceeding_limit(
            user_id=user_id,
            limit=auth_config.active_session_limit - 1,
        )

        for session in sessions:
            await session_storage.delete_session(
                session_id=session.id,
            )

    session = await user_session_dao.insert_session(
        user_id=user_id,
        created_ip=ip_address,
    )

    secret = generate_urlsafe_token()
    secret_hash = compute_scoped_hmac(
        value=secret,
        secret=config.security.tokens.secret_key,
        scope="user_authorization",
    )

    storage_data = map_user_session_to_storage_dto(session, secret_hash)

    await session_storage.save_session(
        session_id=session.id,
        payload=asdict(storage_data),
        ttl=auth_config.expires_interval,
    )

    return UserSessionCreateResult(
        session_key=f"{session.id!s}:{secret}",
        storage=storage_data,
    )


async def verify_session(
    session_id: uuid.UUID,
    secret: str,
) -> UserSessionStorageDTO:
    config = get_config()
    auth_config = config.context.user.authorization.session

    raw_data = await session_storage.get_session_data(
        session_id=session_id,
    )

    if raw_data is None:
        raise UnauthorizedError()

    storage_data = map_storage_dict_to_storage_dto(raw_data)

    secret_hash = compute_scoped_hmac(
        value=secret,
        secret=config.security.tokens.secret_key,
        scope="user_authorization",
    )

    if storage_data.secret_hash != secret_hash:
        raise UnauthorizedError()

    if auth_config.auto_renewal:
        await session_storage.update_session_expire(
            session_id=session_id,
            ttl=auth_config.expires_interval,
        )

    return storage_data


async def update_session_expire(
    *,
    session_id: uuid.UUID,
) -> None:
    config = get_config().context.user.authorization.session
    await session_storage.update_session_expire(
        session_id=session_id,
        ttl=config.expires_interval,
    )


async def delete_session(
    *,
    session_id: uuid.UUID,
) -> None:
    await user_session_dao.soft_delete_session_by_id(session_id)
    await session_storage.delete_session(
        session_id=session_id,
    )


async def delete_user_sessions(
    user_id: int,
    exclude_id: uuid.UUID | None = None,
) -> None:
    sessions = await user_session_dao.soft_delete_user_sessions(
        user_id=user_id,
        exclude_id=exclude_id,
    )
    for session in sessions:
        await session_storage.delete_session(
            session_id=session.id,
        )
