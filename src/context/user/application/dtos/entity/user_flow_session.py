import uuid

from pydantic import BaseModel

from context.user.application.enums.user_flow_session import UserFlowSessionKind

type UserFlowSessionAnyStorageDTO = UserFlowSessionEmailVerificationDTO | UserFlowSessionPasswordResetDTO


class UserFlowSessionEmailVerificationDTO(BaseModel):
    session_id: uuid.UUID
    user_id: int | None
    kind: UserFlowSessionKind
    secret_hash: str


class UserFlowSessionPasswordResetDTO(BaseModel):
    session_id: uuid.UUID
    user_id: int | None
    kind: UserFlowSessionKind
    secret_hash: str
    is_confirmed: bool
