import uuid

from typing import Any

from context.user.application.dtos.entity.user_session import (
    UserSessionDTO,
    UserSessionStorageDTO,
)


def map_user_session_to_storage_dto(
    session: UserSessionDTO,
    secret_hash: str,
) -> UserSessionStorageDTO:
    return UserSessionStorageDTO(
        session_id=session.id,
        user_id=session.user_id,
        secret_hash=secret_hash,
    )


def map_storage_dict_to_storage_dto(
    raw_data: dict[str, Any],
) -> UserSessionStorageDTO:
    session_id = uuid.UUID(raw_data["session_id"])
    user_id = raw_data["user_id"]
    secret_hash = raw_data["secret_hash"]

    return UserSessionStorageDTO(
        session_id=session_id,
        user_id=user_id,
        secret_hash=secret_hash,
    )
