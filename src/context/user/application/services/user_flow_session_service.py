import uuid

from typing import Any, Literal, overload

from config.runtime.loader import get_config
from context.user.application.dtos.entity.user_flow_session import (
    UserFlowSessionAnyStorageDTO,
    UserFlowSessionEmailVerificationDTO,
    UserFlowSessionPasswordResetDTO,
)
from context.user.application.dtos.result.user_flow_session import (
    UserFlowSessionCreateResult,
)
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.infra.storage import session_flow_storage
from shared.errors.authorization import UnauthorizedError
from shared.security.hash import compute_scoped_hmac
from shared.security.tokens import generate_urlsafe_token


@overload
async def create_flow_session(
    user_id: int | None,
    kind: Literal[UserFlowSessionKind.EMAIL_VERIFICATION],
) -> UserFlowSessionCreateResult[UserFlowSessionEmailVerificationDTO]: ...


@overload
async def create_flow_session(
    user_id: int | None,
    kind: Literal[UserFlowSessionKind.PASSWORD_RESET],
    *,
    is_confirmed: bool,
) -> UserFlowSessionCreateResult[UserFlowSessionPasswordResetDTO]: ...


async def create_flow_session(
    user_id: int | None,
    kind: UserFlowSessionKind,
    *,
    is_confirmed: bool | None = None,
) -> UserFlowSessionCreateResult[Any]:
    config = get_config()
    flow_config = config.context.user.get_flow_session_config_by_kind(kind)

    session_id = uuid.uuid4()
    secret = generate_urlsafe_token()
    secret_hash = compute_scoped_hmac(
        value=secret,
        secret=config.security.tokens.secret_key,
        scope=kind.value,
    )

    payload_kwargs: dict[str, Any] = {}

    if kind == UserFlowSessionKind.PASSWORD_RESET:
        payload_kwargs["is_confirmed"] = is_confirmed

    storage_data = _get_flow_session_cls(kind)(
        session_id=session_id,
        user_id=user_id,
        kind=kind,
        secret_hash=secret_hash,
        **payload_kwargs,
    )

    await session_flow_storage.save_session(
        kind=kind,
        session_id=storage_data.session_id,
        payload=storage_data.model_dump(mode="json"),
        ttl=flow_config.expires_interval,
    )

    return UserFlowSessionCreateResult(
        session_key=f"{storage_data.session_id!s}:{secret}",
        storage=storage_data,
    )


@overload
async def verify_flow_session(
    session_id: uuid.UUID,
    secret: str,
    kind: Literal[UserFlowSessionKind.EMAIL_VERIFICATION],
) -> UserFlowSessionEmailVerificationDTO: ...


@overload
async def verify_flow_session(
    session_id: uuid.UUID,
    secret: str,
    kind: Literal[UserFlowSessionKind.PASSWORD_RESET],
) -> UserFlowSessionPasswordResetDTO: ...


@overload
async def verify_flow_session(
    session_id: uuid.UUID,
    secret: str,
    kind: UserFlowSessionKind,
) -> UserFlowSessionAnyStorageDTO: ...


async def verify_flow_session(
    session_id: uuid.UUID,
    secret: str,
    kind: UserFlowSessionKind,
) -> UserFlowSessionAnyStorageDTO:
    config = get_config()
    raw_data = await session_flow_storage.get_session_data(
        session_id=session_id,
        kind=kind,
    )

    if raw_data is None:
        raise UnauthorizedError()

    storage_data = _get_flow_session_cls(kind)(**raw_data)

    secret_hash = compute_scoped_hmac(
        value=secret,
        secret=config.security.tokens.secret_key,
        scope=kind.value,
    )

    if storage_data.secret_hash != secret_hash:
        raise UnauthorizedError()

    return storage_data


async def update_flow_session_expire(
    *,
    session_id: uuid.UUID,
    kind: UserFlowSessionKind,
) -> None:
    config = get_config().context.user.get_flow_session_config_by_kind(kind)
    await session_flow_storage.update_session_expire(
        session_id=session_id,
        kind=kind,
        ttl=config.expires_interval,
    )


async def update_flow_session_data(
    storage_data: UserFlowSessionAnyStorageDTO,
) -> None:
    await session_flow_storage.update_session_data(
        session_id=storage_data.session_id,
        kind=storage_data.kind,
        payload=storage_data.model_dump(mode="json"),
    )


async def delete_flow_session(
    *,
    session_id: uuid.UUID,
    kind: UserFlowSessionKind,
) -> None:
    await session_flow_storage.delete_session(
        kind=kind,
        session_id=session_id,
    )


def _get_flow_session_cls(
    kind: UserFlowSessionKind,
) -> type[UserFlowSessionEmailVerificationDTO] | type[UserFlowSessionPasswordResetDTO]:
    match kind:
        case UserFlowSessionKind.EMAIL_VERIFICATION:
            return UserFlowSessionEmailVerificationDTO
        case UserFlowSessionKind.PASSWORD_RESET:
            return UserFlowSessionPasswordResetDTO
        case _:
            raise ValueError(f"Unsupported flow session kind: {kind!r}")
