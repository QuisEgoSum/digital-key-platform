from context.user.application.dtos.entity.user_action_token import (
    UserActionTokenDTO,
    UserActionTokenGeneratedDTO,
)
from context.user.application.dtos.entity.user_email import UserEmailDTO
from shared.utils.logger import get_logger

logger = get_logger(__name__)


async def send_email_verification_email(
    user_email: UserEmailDTO,
    action_token: UserActionTokenDTO,
    token_generated: UserActionTokenGeneratedDTO,
) -> None:
    # Stub
    logger.info(
        "Sending email verification email",
        email=user_email,
        token=action_token,
        token_generated=token_generated,
    )


async def send_user_password_reset_email(
    user_email: UserEmailDTO,
    action_token: UserActionTokenDTO,
    token_generated: UserActionTokenGeneratedDTO,
) -> None:
    # Stub
    logger.info(
        "Sending user password reset",
        email=user_email,
        token=action_token,
        token_generated=token_generated,
    )
