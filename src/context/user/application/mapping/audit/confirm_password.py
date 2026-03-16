from context.user.application.dtos.command.auth import (
    UserConfirmPasswordByCodeCommand,
    UserConfirmPasswordByLinkCommand,
    UserPasswordResetCommand,
    UserRequestPasswordResetCommand,
)
from context.user.application.dtos.entity.user_action_token import UserActionTokenDTO
from context.user.application.dtos.entity.user_email import UserEmailDTO
from context.user.application.dtos.entity.user_flow_session import (
    UserFlowSessionPasswordResetDTO,
)
from context.user.application.dtos.entity.user_session import UserSessionStorageDTO
from context.user.application.errors.auth import PasswordResetSessionNotConfirmedError
from context.user.application.errors.user_action_token import (
    InvalidUserActionTokenError,
)
from context.user.application.errors.user_email import (
    UserEmailNotFoundError,
    UserEmailNotPrimaryError,
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
from shared.errors.base import ApplicationError


def map_request_password_reset_success(
    *,
    command: UserRequestPasswordResetCommand,
    user_email: UserEmailDTO,
    action_token: UserActionTokenDTO,
    flow_session: UserFlowSessionPasswordResetDTO,
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.ANONYMOUS,
        actor_key=None,
        subject_type=AuditSubjectType.USER,
        subject_id=user_email.user_id,
        scope_type=AuditScopeType.USER,
        scope_id=user_email.user_id,
        result=AuditResultType.SUCCESS,
        action=AuditActionType.PASSWORD_RESET_REQUEST,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "request_accepted",
                "email": command.email,
            },
            entities=[
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_EMAIL,
                    id=user_email.id,
                    role=AuditEventEntityRoleType.RELATED,
                ),
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_ACTION_TOKEN,
                    id=action_token.id,
                    role=AuditEventEntityRoleType.RESULT,
                ),
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_FLOW_SESSION,
                    id=flow_session.session_id,
                    role=AuditEventEntityRoleType.RELATED,
                    extra={"kind": flow_session.kind},
                ),
            ],
        ),
    )


def map_request_password_reset_failure(
    *,
    command: UserRequestPasswordResetCommand,
    user_email: UserEmailDTO | None,
    flow_session: UserFlowSessionPasswordResetDTO | None,
    error: ApplicationError,
) -> AuditEventCommand:
    result = AuditResultType.FAILURE
    if isinstance(error, UserEmailNotFoundError):
        result = AuditResultType.REJECTED
        outcome = "user_not_found"
    elif isinstance(error, UserEmailNotPrimaryError):
        result = AuditResultType.REJECTED
        outcome = "email_not_primary"
    else:
        outcome = "unclassified_error"

    subject_type = None
    user_id = None
    scope_type = None
    scope_id = None

    entities = []

    if flow_session is not None:
        if flow_session.user_id is not None:
            subject_type = AuditSubjectType.USER
            user_id = flow_session.user_id
            scope_type = AuditScopeType.USER
            scope_id = flow_session.user_id
        entities.append(
            AuditEntityRefDTO(
                type=AuditEntityType.USER_FLOW_SESSION,
                id=flow_session.session_id,
                role=AuditEventEntityRoleType.FLOW,
                extra={"kind": flow_session.kind},
            ),
        )

    if user_email is not None:
        subject_type = AuditSubjectType.USER
        user_id = user_email.user_id
        scope_type = AuditScopeType.USER
        scope_id = user_email.user_id
        entities.append(
            AuditEntityRefDTO(
                type=AuditEntityType.USER_EMAIL,
                id=user_email.id,
                role=AuditEventEntityRoleType.RELATED,
            ),
        )

    return AuditEventCommand(
        actor_type=AuditActorType.ANONYMOUS,
        actor_key=None,
        subject_type=subject_type,
        subject_id=user_id,
        scope_type=scope_type,
        scope_id=scope_id,
        result=result,
        action=AuditActionType.PASSWORD_RESET_REQUEST,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": outcome,
                "email": command.email,
                "error_code": error.code,
            },
            entities=entities,
        ),
    )


def map_confirm_password_by_code_success(
    command: UserConfirmPasswordByCodeCommand,
    action_token: UserActionTokenDTO,
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.USER,
        actor_key=action_token.user_id,
        subject_type=AuditSubjectType.USER_ACTION_TOKEN,
        subject_id=action_token.id,
        scope_type=AuditScopeType.USER,
        scope_id=action_token.user_id,
        result=AuditResultType.SUCCESS,
        action=AuditActionType.PASSWORD_RESET_CONFIRM,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "confirmed",
                "flow": "code",
            },
            entities=[
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_FLOW_SESSION,
                    id=command.flow_session.session_id,
                    role=AuditEventEntityRoleType.FLOW,
                    extra={"kind": command.flow_session.kind},
                ),
            ],
        ),
    )


def map_confirm_password_by_code_failure(
    command: UserConfirmPasswordByCodeCommand,
    error: InvalidUserActionTokenError,
) -> AuditEventCommand:
    actor_type = AuditActorType.ANONYMOUS
    actor_key = None
    subject_type = None
    subject_id = None
    scope_type = None
    scope_id = None
    entities: list[AuditEntityRefDTO] = [
        AuditEntityRefDTO(
            type=AuditEntityType.USER_FLOW_SESSION,
            id=command.flow_session.session_id,
            role=AuditEventEntityRoleType.FLOW,
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
        actor_type = AuditActorType.USER
        actor_key = error.action_token.user_id
        result = AuditResultType.REJECTED
        subject_type = AuditSubjectType.USER_ACTION_TOKEN
        subject_id = error.action_token.id
        scope_type = AuditScopeType.USER
        scope_id = error.action_token.user_id

    return AuditEventCommand(
        actor_type=actor_type,
        actor_key=actor_key,
        subject_type=subject_type,
        subject_id=subject_id,
        scope_type=scope_type,
        scope_id=scope_id,
        result=result,
        action=AuditActionType.PASSWORD_RESET_CONFIRM,
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


def map_confirm_password_by_link_success(
    command: UserConfirmPasswordByLinkCommand,
    action_token: UserActionTokenDTO,
    flow_session: UserFlowSessionPasswordResetDTO,
) -> AuditEventCommand:
    return AuditEventCommand(
        actor_type=AuditActorType.USER,
        actor_key=action_token.user_id,
        subject_type=AuditSubjectType.USER_ACTION_TOKEN,
        subject_id=action_token.id,
        scope_type=AuditScopeType.USER,
        scope_id=action_token.user_id,
        result=AuditResultType.SUCCESS,
        action=AuditActionType.PASSWORD_RESET_CONFIRM,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "confirmed",
                "flow": "link",
            },
            entities=[
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_FLOW_SESSION,
                    id=flow_session.session_id,
                    # The flow session is related context for the event.
                    role=AuditEventEntityRoleType.RELATED,
                    extra={"kind": flow_session.kind},
                ),
            ],
        ),
    )


def map_confirm_password_by_link_failure(
    command: UserConfirmPasswordByLinkCommand,
    error: InvalidUserActionTokenError,
) -> AuditEventCommand:
    subject_type: AuditSubjectType | None = None
    subject_id: int | None = None
    scope_type: AuditScopeType | None = None
    scope_id: int | None = None
    result: AuditResultType = AuditResultType.FAILURE
    entities: list[AuditEntityRefDTO] = []

    if command.flow_session is not None:
        if command.flow_session.user_id is not None:
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

    if error.action_token is not None:
        scope_type = AuditScopeType.USER
        scope_id = error.action_token.user_id
        subject_type = AuditSubjectType.USER_ACTION_TOKEN
        subject_id = error.action_token.id

        result = AuditResultType.REJECTED

    return AuditEventCommand(
        actor_type=AuditActorType.ANONYMOUS,
        subject_type=subject_type,
        subject_id=subject_id,
        scope_type=scope_type,
        scope_id=scope_id,
        result=result,
        action=AuditActionType.PASSWORD_RESET_CONFIRM,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": error.classifier,
                "flow": "link",
                "error_code": error.code,
            },
            entities=entities,
        ),
    )


def map_password_reset_success(
    command: UserPasswordResetCommand,
    auth_session: UserSessionStorageDTO | None,
) -> AuditEventCommand:
    entities: list[AuditEntityRefDTO] = [
        AuditEntityRefDTO(
            type=AuditEntityType.USER_FLOW_SESSION,
            id=command.flow_session.session_id,
            role=AuditEventEntityRoleType.FLOW,
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
        actor_key=command.flow_session.user_id,
        subject_type=AuditSubjectType.USER_CREDENTIALS,
        subject_id=command.flow_session.user_id,
        scope_type=AuditScopeType.USER,
        scope_id=command.flow_session.user_id,
        result=AuditResultType.SUCCESS,
        action=AuditActionType.PASSWORD_CHANGE,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": "set_password",
            },
            entities=entities,
        ),
    )


def map_password_reset_failure(
    command: UserPasswordResetCommand,
    error: PasswordResetSessionNotConfirmedError,
) -> AuditEventCommand:
    result = AuditResultType.REJECTED
    outcome = "flow_session_not_confirmed"
    if command.flow_session.user_id is None:
        result = AuditResultType.FAILURE
        outcome = "flow_session_not_bound"

    subject_type: AuditSubjectType | None = None
    subject_id: int | None = None
    scope_type: AuditScopeType | None = None
    scope_id: int | None = None

    if command.flow_session.user_id is not None:
        subject_type = AuditSubjectType.USER_CREDENTIALS
        scope_type = AuditScopeType.USER
        subject_id = scope_id = command.flow_session.user_id

    return AuditEventCommand(
        actor_type=AuditActorType.ANONYMOUS,
        actor_key=None,
        subject_type=subject_type,
        subject_id=subject_id,
        scope_type=scope_type,
        scope_id=scope_id,
        result=result,
        action=AuditActionType.PASSWORD_CHANGE,
        ip_address=command.ip_address,
        data=AuditEventDetailsDTO(
            details={
                "outcome": outcome,
                "error_code": error.code,
            },
            entities=[
                AuditEntityRefDTO(
                    type=AuditEntityType.USER_FLOW_SESSION,
                    id=command.flow_session.session_id,
                    role=AuditEventEntityRoleType.FLOW,
                    extra={"kind": command.flow_session.kind},
                ),
            ],
        ),
    )
