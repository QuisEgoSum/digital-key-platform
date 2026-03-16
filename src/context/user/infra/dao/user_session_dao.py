import uuid

from collections.abc import Sequence

from sqlalchemy import and_, select, update
from sqlalchemy.dialects.postgresql import insert

from context.user.application.dtos.entity.user_session import UserSessionDTO
from context.user.infra.models import UserSessionRow
from infra.persistence.postgresql.connection import db
from infra.persistence.sqlalchemy.mapping import (
    mapping_all_result_to_dto,
    mapping_one_result_to_dto,
)


async def insert_session(
    user_id: int,
    created_ip: str | None,
) -> UserSessionDTO:
    stmt = (
        insert(UserSessionRow)
        .values(
            user_id=user_id,
            created_ip=created_ip,
        )
        .returning(UserSessionRow.__table__)
    )
    result = await db.execute(stmt)
    return mapping_one_result_to_dto(result, UserSessionDTO)


async def soft_delete_session_by_id(session_id: uuid.UUID) -> None:
    stmt = (
        update(UserSessionRow)
        .values(is_deleted=True)
        .where(
            and_(
                UserSessionRow.id == session_id,
                UserSessionRow.is_deleted.is_(False),
            ),
        )
    )
    await db.execute(stmt)


async def soft_delete_user_sessions(
    *,
    user_id: int,
    exclude_id: uuid.UUID | None = None,
) -> Sequence[UserSessionDTO]:
    where = [
        UserSessionRow.user_id == user_id,
        UserSessionRow.is_deleted.is_(False),
    ]

    if exclude_id is not None:
        where.append(UserSessionRow.id != exclude_id)

    stmt = (
        update(UserSessionRow)
        .values(is_deleted=True)
        .where(and_(*where))
        .returning(UserSessionRow.__table__)
    )

    result = await db.execute(stmt)
    return mapping_all_result_to_dto(result, UserSessionDTO)


async def soft_delete_user_sessions_exceeding_limit(
    user_id: int,
    limit: int,
) -> Sequence[UserSessionDTO]:
    sq = (
        select(UserSessionRow.id)
        .where(
            UserSessionRow.user_id == user_id,
            UserSessionRow.is_deleted.is_(False),
        )
        .order_by(UserSessionRow.created_at.desc())
        .offset(limit)
    )

    stmt = (
        update(UserSessionRow)
        .values(is_deleted=True)
        .where(UserSessionRow.id.in_(sq))
        .returning(UserSessionRow.__table__)
    )

    result = await db.execute(stmt)
    return mapping_all_result_to_dto(result, UserSessionDTO)
