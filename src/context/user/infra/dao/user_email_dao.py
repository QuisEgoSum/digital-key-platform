from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.errors.user_email import UserEmailAlreadyExistsError
from context.user.infra.models import UserEmailRow
from infra.persistence.postgresql.connection import db
from infra.persistence.postgresql.utils import is_unique_error
from infra.persistence.sqlalchemy.mapping import mapping_one_result_to_dto


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
