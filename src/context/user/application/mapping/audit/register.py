from context.user.application.dtos.command.auth import UserRegisterCommand
from context.user.application.dtos.entity.user import UserDTO
from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.dtos.entity.user_flow_session import (
    UserFlowSessionEmailVerificationDTO,
)
from infra.audit.dtos import AuditEntityRefDTO, AuditEventCommand, AuditEventDetailsDTO
from infra.audit.enums import (
    AuditActionType,
    AuditActorType,
    AuditEntityType,
    AuditEventEntityRoleType,
    AuditResultType,
    AuditScopeType,
    AuditSubjectType,
)


def map_register_event_success(
    command: UserRegisterCommand,
    user: UserDTO,
    user_email: UserEmailDTO,
    flow_session: UserFlowSessionEmailVerificationDTO,
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.ANONYMOUS,
        subject_type=AuditSubjectType.USER,
        subject_id=user.id,
        subject_extra={"email": command.email},
        scope_type=AuditScopeType.USER,
        scope_id=user.id,
        result=AuditResultType.SUCCESS,
        action=AuditActionType.REGISTER,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "email_verification_required",
            },
            entities=[
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_EMAIL,
                    id=user_email.id,
                    role=AuditEventEntityRoleType.RESULT,
                ),
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_FLOW_SESSION,
                    id=flow_session.session_id,
                    role=AuditEventEntityRoleType.FLOW,
                    extra={"kind": flow_session.kind},
                ),
            ],
        ),
    )


def map_register_event_failure(
    command: UserRegisterCommand,
    flow_session: UserFlowSessionEmailVerificationDTO,
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.ANONYMOUS,
        subject_type=AuditSubjectType.USER,
        subject_extra={"email": command.email},
        scope_type=None,
        scope_id=None,
        result=AuditResultType.REJECTED,
        action=AuditActionType.REGISTER,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "email_already_exists",
            },
            entities=[
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_FLOW_SESSION,
                    id=flow_session.session_id,
                    role=AuditEventEntityRoleType.FLOW,
                    extra={"kind": flow_session.kind},
                ),
            ],
        ),
    )
