from dataclasses import dataclass

import pytest

from context.user.application.dtos.entity.user_action_token import (
    UserActionTokenDTO,
    UserActionTokenGeneratedDTO,
)
from context.user.application.dtos.entity.user_flow_session import (
    UserFlowSessionEmailVerificationDTO,
)
from context.user.application.dtos.result.user_flow_session import (
    UserFlowSessionCreateResult,
)
from context.user.application.enums.user_action_token import (
    UserActionTokenChannelType,
    UserActionTokenKind,
)
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.services import (
    user_action_token_service,
    user_flow_session_service,
)
from infra.persistence.postgresql.connection import DBContext


@dataclass()
class CreateVerificationFlowResult:
    action_token: UserActionTokenDTO
    action_token_generated: UserActionTokenGeneratedDTO
    flow_session: UserFlowSessionCreateResult[UserFlowSessionEmailVerificationDTO]


@dataclass()
class UserAuthFactory:
    db: DBContext

    async def create_email_verification_flow(
        self,
        user_id: int,
        email_id: int,
    ) -> CreateVerificationFlowResult:
        async with self.db.transaction():
            action_token, action_token_generated = (
                await user_action_token_service.create_action_token(
                    user_id=user_id,
                    kind=UserActionTokenKind.EMAIL_VERIFICATION,
                    channel=UserActionTokenChannelType.EMAIL,
                    channel_id=email_id,
                )
            )

        flow_session = await user_flow_session_service.create_flow_session(
            user_id=user_id,
            kind=UserFlowSessionKind.EMAIL_VERIFICATION,
        )

        return CreateVerificationFlowResult(
            action_token=action_token,
            action_token_generated=action_token_generated,
            flow_session=flow_session,
        )


@pytest.fixture()
def user_auth_factory(
    db_context: DBContext,
) -> UserAuthFactory:
    return UserAuthFactory(db_context)
