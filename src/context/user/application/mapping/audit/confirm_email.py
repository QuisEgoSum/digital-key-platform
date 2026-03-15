from context.user.application.dtos.command.auth import (
    UserConfirmEmailByCodeCommand,
    UserConfirmEmailByLinkCommand,
)
from context.user.application.dtos.entity.user_action_token import UserActionTokenDTO
from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.dtos.entity.user_flow_session import (
    UserFlowSessionEmailVerificationDTO,
)
from context.user.application.dtos.entity.user_session import UserSessionStorageDTO
from context.user.application.errors.user_action_token import (
    InvalidUserActionTokenError,
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


def map_request_confirm_email_success(
    *,
    user_id: int,
    ip_address: str,
    user_email: UserEmailDTO,
    action_token: UserActionTokenDTO,
    flow_session: UserFlowSessionEmailVerificationDTO,
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.USER,
        actor_key=user_id,
        subject_type=AuditSubjectType.USER_EMAIL,
        subject_id=user_email.id,
        scope_type=AuditScopeType.USER,
        scope_id=user_email.user_id,
        result=AuditResultType.SUCCESS,
        action=AuditActionType.EMAIL_VERIFICATION_REQUEST,
        ip_address=ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "request_accepted",
            },
            entities=[
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_ACTION_TOKEN,
                    id=action_token.id,
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


def map_request_confirm_email_suppressed(
    *,
    ip_address: str,
    flow_session: UserFlowSessionEmailVerificationDTO,
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.ANONYMOUS,
        actor_key=None,
        subject_type=None,
        subject_id=None,
        scope_type=AuditScopeType.USER if flow_session.user_id else None,
        scope_id=flow_session.user_id,
        result=AuditResultType.REJECTED,
        action=AuditActionType.EMAIL_VERIFICATION_REQUEST,
        ip_address=ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "flow_session_not_bound",
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


def map_confirm_email_by_code_success(
    command: UserConfirmEmailByCodeCommand,
    action_token: UserActionTokenDTO,
    auth_session: UserSessionStorageDTO | None,
) -> AuditEventCommand:
    entities = [
        AuditEntityRefDTO(
            type=AuditEntityType.USER_ACTION_TOKEN,
            id=action_token.id,
            role=AuditEventEntityRoleType.RELATED,
        ),
        AuditEntityRefDTO(
            type=AuditEntityType.USER_FLOW_SESSION,
            id=command.flow_session.session_id,
            role=AuditEventEntityRoleType.SOURCE,
            extra={"kind": command.flow_session.kind},
        ),
    ]

    if auth_session is not None:
        entities.append(
            AuditEntityRefDTO(
                type=AuditEntityType.USER_SESSION,
                id=auth_session.session_id,
                role=AuditEventEntityRoleType.RESULT,
            ),
        )

    return AuditEventCommand(
        actor_type=AuditActorType.USER,
        actor_key=action_token.user_id,
        subject_type=AuditSubjectType.USER_EMAIL,
        subject_id=action_token.channel_id,
        scope_type=AuditScopeType.USER,
        scope_id=action_token.user_id,
        result=AuditResultType.SUCCESS,
        action=AuditActionType.EMAIL_VERIFICATION_CONFIRM,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "email_verified",
                "flow": "code",
            },
            entities=entities,
        ),
    )


def map_confirm_email_by_code_failure(
    command: UserConfirmEmailByCodeCommand,
    error: InvalidUserActionTokenError,
) -> AuditEventCommand:
    actor_type: AuditActorType = AuditActorType.ANONYMOUS
    actor_key = None
    subject_type: AuditSubjectType | None = None
    subject_id: int | None = None
    scope_type = None
    scope_id = None
    entities: list[AuditEntityRefDTO] = [
        AuditEntityRefDTO(
            type=AuditEntityType.USER_FLOW_SESSION,
            id=command.flow_session.session_id,
            role=AuditEventEntityRoleType.SOURCE,
            extra={"kind": command.flow_session.kind},
        ),
    ]
    result: AuditResultType = AuditResultType.FAILURE

    if command.flow_session.user_id is not None:
        actor_type = AuditActorType.USER
        actor_key = command.flow_session.user_id
        scope_type = AuditScopeType.USER
        scope_id = command.flow_session.user_id

    if error.action_token is not None:
        subject_type = AuditSubjectType.USER_EMAIL
        subject_id = error.action_token.channel_id
        scope_type = AuditScopeType.USER
        scope_id = error.action_token.user_id
        result = AuditResultType.REJECTED
        entities.append(
            AuditEntityRefDTO(
                type=AuditEntityType.USER_ACTION_TOKEN,
                id=error.action_token.id,
                role=AuditEventEntityRoleType.RELATED,
            ),
        )

    return AuditEventCommand(
        actor_type=actor_type,
        actor_key=actor_key,
        subject_type=subject_type,
        subject_id=subject_id,
        scope_type=scope_type,
        scope_id=scope_id,
        result=result,
        action=AuditActionType.EMAIL_VERIFICATION_CONFIRM,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": error.classifier,
                "flow": "code",
                "error_code": error.code,
            },
            entities=entities,
        ),
    )


def map_confirm_email_by_link_success(
    command: UserConfirmEmailByLinkCommand,
    action_token: UserActionTokenDTO,
    auth_session: UserSessionStorageDTO | None,
) -> AuditEventCommand:
    entities: list[AuditEntityRefDTO] = [
        AuditEntityRefDTO(
            type=AuditEntityType.USER_ACTION_TOKEN,
            id=action_token.id,
            role=AuditEventEntityRoleType.RELATED,
        ),
    ]

    if command.flow_session is not None:
        entities.append(
            AuditEntityRefDTO(
                type=AuditEntityType.USER_FLOW_SESSION,
                id=command.flow_session.session_id,
                # The flow session is related context for the event.
                role=AuditEventEntityRoleType.RELATED,
                extra={"kind": command.flow_session.kind},
            ),
        )

    if auth_session is not None:
        entities.append(
            AuditEntityRefDTO(
                type=AuditEntityType.USER_SESSION,
                id=auth_session.session_id,
                role=AuditEventEntityRoleType.RESULT,
            ),
        )

    return AuditEventCommand(
        actor_type=AuditActorType.USER,
        actor_key=action_token.user_id,
        subject_type=AuditSubjectType.USER_EMAIL,
        subject_id=action_token.channel_id,
        scope_type=AuditScopeType.USER,
        scope_id=action_token.user_id,
        result=AuditResultType.SUCCESS,
        action=AuditActionType.EMAIL_VERIFICATION_CONFIRM,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "email_verified",
                "flow": "link",
            },
            entities=entities,
        ),
    )


def map_confirm_email_by_link_failure(
    command: UserConfirmEmailByLinkCommand,
    error: InvalidUserActionTokenError,
) -> AuditEventCommand:
    scope_type: AuditScopeType | None = None
    scope_id: int | None = None
    entities: list[AuditEntityRefDTO] = []
    data = AuditEventDetailsDTO(
        details={
            "outcome": error.classifier,
            "flow": "link",
            "error_code": error.code,
        },
        entities=entities,
    )

    if command.flow_session is not None:
        if command.flow_session.user_id:
            scope_type = AuditScopeType.USER
            scope_id = command.flow_session.user_id
        entities.append(
            AuditEntityRefDTO(
                type=AuditEntityType.USER_FLOW_SESSION,
                id=command.flow_session.session_id,
                # The flow session is related context for the event.
                role=AuditEventEntityRoleType.RELATED,
                extra={"kind": command.flow_session.kind},
            ),
        )

    if error.action_token is None:
        return AuditEventCommand(
            actor_type=AuditActorType.ANONYMOUS,
            actor_key=None,
            subject_type=None,
            subject_id=None,
            scope_type=scope_type,
            scope_id=scope_id,
            result=AuditResultType.FAILURE,
            action=AuditActionType.EMAIL_VERIFICATION_CONFIRM,
            ip_address=command.ip_address,
            data=data,
        )

    scope_type = AuditScopeType.USER
    scope_id = error.action_token.user_id
    entities.append(
        AuditEntityRefDTO(
            type=AuditEntityType.USER_ACTION_TOKEN,
            id=error.action_token.id,
            role=AuditEventEntityRoleType.RELATED,
        ),
    )

    return AuditEventCommand(
        actor_type=AuditActorType.ANONYMOUS,
        actor_key=None,
        subject_type=AuditSubjectType.USER_EMAIL,
        subject_id=error.action_token.channel_id,
        scope_type=scope_type,
        scope_id=scope_id,
        result=AuditResultType.REJECTED,
        action=AuditActionType.EMAIL_VERIFICATION_CONFIRM,
        ip_address=command.ip_address,
        data=data,
    )
