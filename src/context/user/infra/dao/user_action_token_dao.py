from collections.abc import Sequence
from dataclasses import asdict

from sqlalchemy import and_, select, update
from sqlalchemy.dialects.postgresql import insert

from context.user.application.dtos.entity.user_action_token import UserActionTokenDTO
from context.user.application.dtos.payload.user_action_token import (
    UserActionTokenInsertPayload,
)
from context.user.application.enums.user_action_token import (
    UserActionTokenKind,
    UserActionTokenStatusType,
)
from context.user.infra.models import UserActionTokenRow
from infra.persistence.postgresql.connection import db
from infra.persistence.sqlalchemy.mapping import (
    mapping_first_result_to_dto,
    mapping_one_result_to_dto,
)


async def cancel_active_user_kind_tokens(
    user_id: int,
    kind: UserActionTokenKind,
) -> Sequence[int]:
    stmt = (
        update(UserActionTokenRow)
        .values(
            status=UserActionTokenStatusType.CANCELED,
        )
        .where(
            and_(
                UserActionTokenRow.user_id == user_id,
                UserActionTokenRow.kind == kind,
                UserActionTokenRow.status == UserActionTokenStatusType.ACTIVE,
            ),
        )
        .returning(UserActionTokenRow.id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def insert_user_action_token(
    payload: UserActionTokenInsertPayload,
) -> UserActionTokenDTO:
    stmt = (
        insert(UserActionTokenRow)
        .values(**asdict(payload))
        .returning(UserActionTokenRow.__table__)
    )
    result = await db.execute(stmt)
    return mapping_one_result_to_dto(result, UserActionTokenDTO)


async def get_active_user_token_by_user_id(
    user_id: int,
    kind: UserActionTokenKind,
) -> UserActionTokenDTO | None:
    stmt = select(UserActionTokenRow.__table__).where(
        and_(
            UserActionTokenRow.user_id == user_id,
            UserActionTokenRow.kind == kind,
            UserActionTokenRow.status == UserActionTokenStatusType.ACTIVE,
        ),
    )
    result = await db.execute(stmt)
    return mapping_first_result_to_dto(result, UserActionTokenDTO)


async def update_token_status(
    token_id: int,
    status: UserActionTokenStatusType,
) -> UserActionTokenDTO:
    stmt = (
        update(UserActionTokenRow)
        .values(status=status)
        .where(UserActionTokenRow.id == token_id)
        .returning(UserActionTokenRow.__table__)
    )
    result = await db.execute(stmt)
    return mapping_one_result_to_dto(result, UserActionTokenDTO)


async def get_active_user_token_by_long_hash(
    long_token_hash: str,
) -> UserActionTokenDTO | None:
    stmt = select(UserActionTokenRow.__table__).where(
        UserActionTokenRow.long_token_hash == long_token_hash,
    )
    result = await db.execute(stmt)
    return mapping_first_result_to_dto(result, UserActionTokenDTO)
