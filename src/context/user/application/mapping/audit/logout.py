from context.user.application.dtos.command.auth import UserLogoutCommand
from infra.audit.dtos import AuditEventCommand
from infra.audit.enums import (
    AuditActionType,
    AuditActorType,
    AuditResultType,
    AuditScopeType,
    AuditSubjectType,
)


def map_logout_event(command: UserLogoutCommand) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.USER,
        actor_key=command.session.user_id,
        subject_type=AuditSubjectType.USER_SESSION,
        subject_id=command.session.session_id,
        scope_type=AuditScopeType.USER,
        scope_id=command.session.user_id,
        result=AuditResultType.SUCCESS,
        action=AuditActionType.LOGOUT,
        ip_address=command.ip_address,
    )
