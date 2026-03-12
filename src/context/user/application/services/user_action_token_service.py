from config import config
from context.user.application.dtos.entity.user_action_token import (
    UserActionTokenDTO,
    UserActionTokenGeneratedDTO,
)
from context.user.application.dtos.payload.user_action_token import (
    UserActionTokenInsertPayload,
)
from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
)
from context.user.config.user_action_token import UserActionTokenConfig
from context.user.infra.dao import user_action_token_dao
from shared.security.hash import compute_scoped_hmac
from shared.security.tokens import generate_numeric_token, generate_urlsafe_token
from shared.utils.datetime_utils import current_datetime
from shared.utils.logger import get_logger

logger = get_logger(__name__)


async def create_action_token(
    user_id: int,
    kind: UserActionTokenKind,
    channel: UserActionTokenChannelType,
    channel_id: int,
) -> tuple[UserActionTokenDTO, UserActionTokenGeneratedDTO]:
    cfg = config.context.user.get_token_config_by_kind(kind)
    token = generate_action_token(cfg, kind)

    cancelled_ids = await user_action_token_dao.cancel_active_user_kind_tokens(
        user_id,
        kind,
    )

    logger.info(
        "Cancelled user action tokens",
        user_id=user_id,
        kind=kind,
        token_ids=cancelled_ids,
    )

    token_dto = await user_action_token_dao.insert_user_action_token(
        UserActionTokenInsertPayload(
            user_id=user_id,
            kind=kind,
            channel_id=channel_id,
            channel=channel,
            short_token_hash=token.short_token_hash,
            long_token_hash=token.long_token_hash,
            expires_at=current_datetime() + cfg.expires_interval,
        ),
    )

    return token_dto, token


def generate_action_token(
    cfg: UserActionTokenConfig,
    kind: UserActionTokenKind,
) -> UserActionTokenGeneratedDTO:
    short_token = generate_numeric_token(length=cfg.short_token_length)
    long_token = generate_urlsafe_token(nbytes=cfg.long_token_bytes)

    return UserActionTokenGeneratedDTO(
        short_token=short_token,
        long_token=long_token,
        short_token_hash=compute_scoped_hmac(
            value=short_token,
            secret=config.security.tokens.secret_key,
            scope=kind.value,
        ),
        long_token_hash=compute_scoped_hmac(
            value=long_token,
            secret=config.security.tokens.secret_key,
            scope=kind.value,
        ),
    )
