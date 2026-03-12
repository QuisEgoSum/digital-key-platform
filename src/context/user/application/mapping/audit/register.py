from typing import Any

from context.user.application.dtos.command.auth import UserRegisterCommand
from context.user.application.dtos.entity.user import UserDTO
from context.user.application.dtos.entity.user_action_token import UserActionTokenDTO
from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.dtos.entity.user_session import UserSessionStorageDTO
from infra.audit.dtos import AuditEntityRefDTO, AuditEventCommand, AuditEventDetailsDTO
from infra.audit.enums import (
    AuditActionType,
    AuditActorType,
    AuditEntityType,
    AuditEventEntityRoleType,
    AuditResultType,
    AuditSubjectType,
)


def map_register_event_success(
    command: UserRegisterCommand,
    user: UserDTO,
    email: UserEmailDTO,
    action_token: UserActionTokenDTO,
    session: UserSessionStorageDTO[Any],
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.ANONYMOUS,
        subject_type=AuditSubjectType.USER,
        subject_id=user.id,
        result=AuditResultType.SUCCESS,
        action=AuditActionType.REGISTER,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "email_verification_required",
            },
            entities=[
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_EMAIL,
                    id=email.id,
                    role=AuditEventEntityRoleType.RESULT,
                ),
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_ACTION_TOKEN,
                    id=action_token.id,
                    role=AuditEventEntityRoleType.RESULT,
                ),
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_SESSION,
                    id=session.session_id,
                    role=AuditEventEntityRoleType.RESULT,
                ),
            ],
            context={
                "ip_address": command.ip_address,
            },
        ),
    )


def map_register_event_failure(
    command: UserRegisterCommand,
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.ANONYMOUS,
        subject_type=AuditSubjectType.USER,
        subject_extra={"email": command.email},
        result=AuditResultType.REJECTED,
        action=AuditActionType.REGISTER,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "email_already_exists",
            },
            context={
                "ip_address": command.ip_address,
            },
        ),
    )
