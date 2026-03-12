import uuid

from typing import Any

from context.user.application.dtos.entity.user_session import (
    UserSessionDTO,
    UserSessionPasswordResetStateDTO,
    UserSessionStorageDTO,
)
from context.user.application.enums.user_session import UserSessionKind

SESSION_STATE_DTOS = {
    UserSessionKind.PASSWORD_RESET: UserSessionPasswordResetStateDTO,
}


def map_user_session_to_storage_dto(
    session: UserSessionDTO,
    secret_hash: str,
) -> UserSessionStorageDTO[object]:
    state: object = None

    if session.kind in SESSION_STATE_DTOS:
        state = SESSION_STATE_DTOS[session.kind]()

    return UserSessionStorageDTO(
        session_id=session.id,
        user_id=session.user_id,
        kind=session.kind,
        state=state,
        secret_hash=secret_hash,
    )


def map_storage_dict_to_storage_dto(
    raw_data: dict[str, Any],
) -> UserSessionStorageDTO[object]:
    session_id = uuid.UUID(raw_data["session_id"])
    user_id = raw_data["user_id"]
    kind = UserSessionKind(raw_data["kind"])
    secret_hash = raw_data["secret_hash"]
    state: object = None

    if kind in SESSION_STATE_DTOS:
        state = SESSION_STATE_DTOS[kind](**raw_data["state"])

    return UserSessionStorageDTO(
        session_id=session_id,
        user_id=user_id,
        kind=kind,
        state=state,
        secret_hash=secret_hash,
    )
