from context.user.application.dtos.entity.user_action_token import (
    UserActionTokenDTO,
    UserActionTokenGeneratedDTO,
)
from context.user.application.dtos.entity.user_email import UserEmailDTO
from shared.utils.logger import get_logger

logger = get_logger(__name__)


async def send_user_registration_email(
    email: UserEmailDTO,
    token: UserActionTokenDTO,
    token_generated: UserActionTokenGeneratedDTO,
) -> None:
    # Stub
    logger.info(
        "Sending user registration email",
        email=email,
        token=token,
        token_generated=token_generated,
    )
