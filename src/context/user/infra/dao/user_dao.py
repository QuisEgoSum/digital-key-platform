from dataclasses import asdict

from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased

from context.user.application.dtos.entity.user import (
    UserDTO,
    UserLoginDetailsDTO,
    UserMeDTO,
)
from context.user.application.dtos.payload.user import UserCreatePayload
from context.user.infra.models import UserCredentialsRow, UserEmailRow, UserRow
from infra.persistence.postgresql.connection import db
from infra.persistence.postgresql.funcs import (
    jsonb_build_array_agg_builder,
    jsonb_object_builder,
)
from infra.persistence.sqlalchemy.mapping import (
    mapping_first_result_to_dto,
    mapping_one_result_to_dto,
)


async def insert_user(
    payload: UserCreatePayload,
) -> UserDTO:
    stmt = insert(UserRow).values(**asdict(payload)).returning(UserRow.__table__)
    result = await db.execute(stmt)
    return mapping_one_result_to_dto(result, UserDTO)


async def get_login_details(email: str) -> UserLoginDetailsDTO | None:
    e = aliased(UserEmailRow, name="e")

    stmt = (
        select(
            UserRow.__table__,
            jsonb_object_builder(UserCredentialsRow).label("credentials"),
            jsonb_build_array_agg_builder(UserEmailRow).label("emails"),
        )
        .select_from(e)
        .join(UserRow, UserRow.id == e.user_id)
        .join(UserCredentialsRow, UserCredentialsRow.user_id == e.user_id)
        .join(
            UserEmailRow,
            and_(
                UserEmailRow.user_id == e.user_id,
                UserEmailRow.revoked_at.is_(None),
            ),
        )
        .where(
            e.email == email,
            e.is_primary.is_(True),
            e.revoked_at.is_(None),
        )
        .group_by(UserRow.id, UserCredentialsRow.user_id)
    )

    result = await db.execute(stmt)

    return mapping_first_result_to_dto(result, UserLoginDetailsDTO)


async def get_user_me(user_id: int) -> UserMeDTO:
    stmt = (
        select(
            UserRow.id,
            UserRow.name,
            UserRow.locale,
            UserRow.timezone,
            UserRow.created_at,
            UserRow.updated_at,
            jsonb_build_array_agg_builder(UserEmailRow).label("emails"),
        )
        .select_from(UserRow)
        .outerjoin(
            UserEmailRow,
            and_(
                UserEmailRow.user_id == UserRow.id,
                UserEmailRow.revoked_at.is_(None),
            ),
        )
        .where(UserRow.id == user_id)
        .group_by(UserRow.id)
    )
    result = await db.execute(stmt)
    return mapping_one_result_to_dto(result, UserMeDTO)
