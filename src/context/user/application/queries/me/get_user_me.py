from context.user.application.dtos.entity.user import UserMeDTO
from context.user.application.services import user_service
from infra.persistence.postgresql.connection import db


async def get_user_me(user_id: int) -> UserMeDTO:
    async with db.session():
        return await user_service.get_user_me(user_id)
