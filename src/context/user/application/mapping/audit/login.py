from typing import Any

from context.user.application.dtos.command.auth import UserLoginCommand
from context.user.application.dtos.entity.user import UserLoginDetailsDTO
from context.user.application.dtos.entity.user_session import UserSessionStorageDTO
from context.user.application.errors.auth import InvalidCredentialsError
from context.user.application.errors.user import (
    UserBannedError,
    UserTemporaryBlockedError,
)
from context.user.application.types.auth import UserLoginStatus
from infra.audit.dtos import AuditEntityRefDTO, AuditEventCommand, AuditEventDetailsDTO
from infra.audit.enums import (
    AuditActionType,
    AuditActorType,
    AuditEntityType,
    AuditEventEntityRoleType,
    AuditResultType,
    AuditSubjectType,
)
from shared.errors.base import ApplicationError


def _get_login_audit_outcome(error: ApplicationError) -> str:
    if isinstance(error, InvalidCredentialsError):
        return error.classifier
    if isinstance(error, UserTemporaryBlockedError):
        return "user_temporary_blocked"
    if isinstance(error, UserBannedError):
        return "user_banned"
    return "unclassified_error"


def map_login_event_anonymous(
    command: UserLoginCommand,
    error: ApplicationError,
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.ANONYMOUS,
        subject_type=AuditSubjectType.USER,
        subject_extra={"email": command.email},
        result=AuditResultType.FAILURE,
        action=AuditActionType.LOGIN,
        data=AuditEventDetailsDTO(
            details={
                "outcome": _get_login_audit_outcome(error),
                "error_code": error.code,
            },
            context={
                "ip_address": command.ip_address,
            },
        ),
    )


def map_login_event_with_session(
    command: UserLoginCommand,
    login_details: UserLoginDetailsDTO,
    session: UserSessionStorageDTO[Any],
    status: UserLoginStatus,
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.USER,
        actor_key=login_details.id,
        subject_type=AuditSubjectType.USER,
        subject_id=login_details.id,
        result=(
            AuditResultType.SUCCESS
            if status == "logged_in"
            else AuditResultType.REJECTED
        ),
        action=AuditActionType.LOGIN,
        data=AuditEventDetailsDTO(
            details={
                "outcome": status,
            },
            entities=[
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


def map_login_event_with_error(
    command: UserLoginCommand,
    login_details: UserLoginDetailsDTO,
    error: ApplicationError,
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.USER,
        actor_key=login_details.id,
        subject_type=AuditSubjectType.USER,
        subject_id=login_details.id,
        result=(
            AuditResultType.REJECTED
            if isinstance(error, (UserBannedError, UserTemporaryBlockedError))
            else AuditResultType.FAILURE
        ),
        action=AuditActionType.LOGIN,
        data=AuditEventDetailsDTO(
            details={
                "outcome": _get_login_audit_outcome(error),
                "error_code": error.code,
            },
            context={
                "ip_address": command.ip_address,
            },
        ),
    )
