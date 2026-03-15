from datetime import datetime

from sqlalchemy import and_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.errors.user_email import UserEmailAlreadyExistsError
from context.user.infra.models import UserEmailRow
from infra.persistence.postgresql.connection import db
from infra.persistence.postgresql.utils import is_unique_error
from infra.persistence.sqlalchemy.mapping import (
    mapping_first_result_to_dto,
    mapping_one_result_to_dto,
)


async def insert_user_email(
    user_id: int,
    email: str,
    is_primary: bool,
) -> UserEmailDTO:
    stmt = (
        insert(UserEmailRow)
        .values(
            user_id=user_id,
            email=email,
            is_primary=is_primary,
        )
        .returning(UserEmailRow.__table__)
    )
    try:
        result = await db.execute(stmt)
    except IntegrityError as ex:
        if is_unique_error(ex):
            raise UserEmailAlreadyExistsError() from ex
        raise

    return mapping_one_result_to_dto(result, UserEmailDTO)


async def set_verified_at(
    email_id: int,
    *,
    verified_at: datetime,
) -> UserEmailDTO | None:
    stmt = (
        update(UserEmailRow)
        .values(verified_at=verified_at)
        .where(
            and_(
                UserEmailRow.id == email_id,
                UserEmailRow.revoked_at.is_(None),
                UserEmailRow.verified_at.is_(None),
            ),
        )
        .returning(UserEmailRow.__table__)
    )
    result = await db.execute(stmt)
    return mapping_first_result_to_dto(result, UserEmailDTO)


async def get_user_primary_email(user_id: int) -> UserEmailDTO | None:
    stmt = select(UserEmailRow.__table__).where(
        and_(
            UserEmailRow.user_id == user_id,
            UserEmailRow.is_primary.is_(True),
            UserEmailRow.revoked_at.is_(None),
        ),
    )
    result = await db.execute(stmt)
    return mapping_first_result_to_dto(result, UserEmailDTO)


async def get_email(email: str) -> UserEmailDTO | None:
    stmt = select(UserEmailRow.__table__).where(
        and_(
            UserEmailRow.email == email,
            UserEmailRow.revoked_at.is_(None),
        ),
    )
    result = await db.execute(stmt)
    return mapping_first_result_to_dto(result, UserEmailDTO)
