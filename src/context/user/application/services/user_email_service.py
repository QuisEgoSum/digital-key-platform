from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.infra.dao import user_email_dao


async def create_user_email(
    user_id: int,
    email: str,
    is_primary: bool,
) -> UserEmailDTO:
    return await user_email_dao.insert_user_email(
        user_id=user_id,
        email=email,
        is_primary=is_primary,
    )
