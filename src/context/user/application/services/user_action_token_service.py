from config.runtime.loader import get_config
from context.user.application.dtos.data.user_action_token import (
    UserActionTokenInsertData,
)
from context.user.application.dtos.entity.user_action_token import (
    UserActionTokenDTO,
    UserActionTokenGeneratedDTO,
)
from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
    UserActionTokenStatusType,
)
from context.user.application.errors.user_action_token import (
    InvalidUserActionTokenError,
)
from context.user.config.user_action_token import UserActionTokenConfig
from context.user.infra.dao import user_action_token_dao
from shared.context.debug_collector import add_debug_artifact
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
    config = get_config()
    flow_config = config.context.user.get_token_config_by_kind(kind)

    token = generate_action_token(
        flow_config=flow_config,
        kind=kind,
        secret_key=config.security.tokens.secret_key,
    )

    add_debug_artifact(f"user-action-token-{kind!s}-short", token.short_token)
    add_debug_artifact(f"user-action-token-{kind!s}-long", token.long_token)

    cancelled_ids = await user_action_token_dao.cancel_active_user_kind_tokens(
        user_id,
        kind,
    )

    if cancelled_ids:
        logger.info(
            "Cancelled user action tokens",
            user_id=user_id,
            kind=kind,
            token_ids=cancelled_ids,
        )

    token_dto = await user_action_token_dao.insert_user_action_token(
        UserActionTokenInsertData(
            user_id=user_id,
            kind=kind,
            channel_id=channel_id,
            channel=channel,
            short_token_hash=token.short_token_hash,
            long_token_hash=token.long_token_hash,
            expires_at=current_datetime() + flow_config.expires_interval,
        ),
    )

    return token_dto, token


def generate_action_token(
    flow_config: UserActionTokenConfig,
    kind: UserActionTokenKind,
    secret_key: str,
) -> UserActionTokenGeneratedDTO:
    short_token = generate_numeric_token(length=flow_config.short_token_length)
    long_token = generate_urlsafe_token(nbytes=flow_config.long_token_bytes)

    return UserActionTokenGeneratedDTO(
        short_token=short_token,
        long_token=long_token,
        short_token_hash=compute_scoped_hmac(
            value=short_token,
            secret=secret_key,
            scope=kind.value,
        ),
        long_token_hash=compute_scoped_hmac(
            value=long_token,
            secret=secret_key,
            scope=kind.value,
        ),
    )


async def verify_short_token(
    user_id: int,
    kind: UserActionTokenKind,
    token: str,
) -> UserActionTokenDTO:
    config = get_config()

    action_token = await user_action_token_dao.get_active_user_token_by_user_id(
        user_id=user_id,
        kind=kind,
    )

    if action_token is None:
        raise InvalidUserActionTokenError("token_not_found")

    if action_token.expires_at < current_datetime():
        raise InvalidUserActionTokenError("token_expired", action_token)

    short_token_hash = compute_scoped_hmac(
        value=token,
        secret=config.security.tokens.secret_key,
        scope=kind.value,
    )

    if action_token.short_token_hash != short_token_hash:
        raise InvalidUserActionTokenError("token_mismatch", action_token)

    return await user_action_token_dao.update_token_status(
        action_token.id,
        status=UserActionTokenStatusType.USED,
    )


async def verify_link_token(
    kind: UserActionTokenKind,
    token: str,
) -> UserActionTokenDTO:
    config = get_config()

    long_token_hash = compute_scoped_hmac(
        value=token,
        secret=config.security.tokens.secret_key,
        scope=kind.value,
    )

    action_token = await user_action_token_dao.get_active_user_token_by_long_hash(
        long_token_hash=long_token_hash,
    )

    if action_token is None:
        raise InvalidUserActionTokenError("token_not_found")

    if action_token.expires_at < current_datetime():
        raise InvalidUserActionTokenError("token_expired", action_token)

    return await user_action_token_dao.update_token_status(
        action_token.id,
        status=UserActionTokenStatusType.USED,
    )
