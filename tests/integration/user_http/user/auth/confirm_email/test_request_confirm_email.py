from http import HTTPStatus

from context.user.application.enums.user_action_token import (
    UserActionTokenKind,
    UserActionTokenStatusType,
)
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.errors.user_email import UserEmailAlreadyVerifiedError
from fixtures.infra.audit import AuditEventQuery
from fixtures.sanic_types import AppSanicTestClient
from fixtures.user.auth import UserAuthFactory
from fixtures.user.user import UserFactory
from fixtures.user.user_action_token import UserActionTokenQuery
from fixtures.user.user_email_agent import UserEmailAgentMock
from infra.audit.enums import (
    AuditActionType,
    AuditActorType,
    AuditEntityType,
    AuditEventEntityRoleType,
    AuditResultType,
    AuditScopeType,
    AuditSubjectType,
)
from shared.errors.authorization import UnauthorizedError
from utils.audit_asserts import audit_event_asserts


async def test_request_confirm_email_success(
    sanic_user_http_client: AppSanicTestClient,
    user_factory: UserFactory,
    user_auth_factory: UserAuthFactory,
    user_action_token_query: UserActionTokenQuery,
    user_email_agent_mock: UserEmailAgentMock,
    audit_event_query: AuditEventQuery,
) -> None:
    created_user = await user_factory.create(verify_email=False)
    user_id = created_user.user.id
    email_id = created_user.email.id

    flow_session = await user_auth_factory.create_email_verification_session(
        user_id=user_id,
    )

    sanic_user_http_client.cookies["ev_session"] = flow_session.session_key

    _, res = await sanic_user_http_client.post("/v1/auth/email/request-verification")

    assert res.status == HTTPStatus.NO_CONTENT

    action_tokens = await user_action_token_query.all()

    assert len(action_tokens) == 1

    action_token = action_tokens[0]

    assert action_token.user_id == user_id
    assert action_token.channel_id == email_id
    assert action_token.status == UserActionTokenStatusType.ACTIVE
    assert action_token.kind == UserActionTokenKind.EMAIL_VERIFICATION

    user_email_agent_mock.send_email_verification_email.assert_called_once()
    _, kwargs = user_email_agent_mock.send_email_verification_email.call_args

    assert kwargs["user_email"].id == email_id
    assert kwargs["action_token"].id == action_token.id

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    event = audit_events[0]

    audit_event_asserts(
        event,
        actor_type=AuditActorType.USER,
        actor_key=user_id,
        subject_type=AuditSubjectType.USER_EMAIL,
        subject_id=email_id,
        scope_type=AuditScopeType.USER,
        scope_id=user_id,
        action=AuditActionType.EMAIL_VERIFICATION_REQUEST,
        result=AuditResultType.SUCCESS,
        entities=[
            {
                "type": AuditEntityType.USER_ACTION_TOKEN,
                "id": action_token.id,
                "role": AuditEventEntityRoleType.RESULT,
                "extra": None,
            },
            {
                "type": AuditEntityType.USER_FLOW_SESSION,
                "id": str(flow_session.storage.session_id),
                "role": AuditEventEntityRoleType.FLOW,
                "extra": {"kind": UserFlowSessionKind.EMAIL_VERIFICATION},
            },
        ],
    )


async def test_request_confirm_email_suppressed(
    sanic_user_http_client: AppSanicTestClient,
    user_auth_factory: UserAuthFactory,
    audit_event_query: AuditEventQuery,
) -> None:
    flow_session = await user_auth_factory.create_email_verification_session(None)

    sanic_user_http_client.cookies["ev_session"] = flow_session.session_key

    _, res = await sanic_user_http_client.post("/v1/auth/email/request-verification")

    assert res.status == HTTPStatus.NO_CONTENT

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    event = audit_events[0]

    audit_event_asserts(
        event,
        actor_type=AuditActorType.ANONYMOUS,
        action=AuditActionType.EMAIL_VERIFICATION_REQUEST,
        result=AuditResultType.REJECTED,
        details={"outcome": "flow_session_not_bound"},
        entities=[
            {
                "type": AuditEntityType.USER_FLOW_SESSION,
                "id": str(flow_session.storage.session_id),
                "role": AuditEventEntityRoleType.FLOW,
                "extra": {"kind": UserFlowSessionKind.EMAIL_VERIFICATION},
            },
        ],
    )


async def test_request_confirm_email_with_already_confirmed(
    sanic_user_http_client: AppSanicTestClient,
    user_factory: UserFactory,
    user_auth_factory: UserAuthFactory,
    audit_event_query: AuditEventQuery,
) -> None:
    created_user = await user_factory.create()
    user_id = created_user.user.id
    flow_session = await user_auth_factory.create_email_verification_session(user_id)

    sanic_user_http_client.cookies["ev_session"] = flow_session.session_key

    _, res = await sanic_user_http_client.post("/v1/auth/email/request-verification")

    assert res.status == HTTPStatus.CONFLICT

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    event = audit_events[0]

    audit_event_asserts(
        event,
        actor_type=AuditActorType.USER,
        actor_key=user_id,
        subject_type=AuditSubjectType.USER_EMAIL,
        subject_id=created_user.email.id,
        scope_type=AuditScopeType.USER,
        scope_id=user_id,
        action=AuditActionType.EMAIL_VERIFICATION_REQUEST,
        result=AuditResultType.REJECTED,
        details={
            "outcome": "email_already_verified",
            "error_code": UserEmailAlreadyVerifiedError.code,
        },
        entities=[
            {
                "type": AuditEntityType.USER_FLOW_SESSION,
                "id": str(flow_session.storage.session_id),
                "role": AuditEventEntityRoleType.FLOW,
                "extra": {"kind": UserFlowSessionKind.EMAIL_VERIFICATION},
            },
        ],
    )


async def test_request_confirm_email_unauthorized(
    sanic_user_http_client: AppSanicTestClient,
) -> None:
    _, res = await sanic_user_http_client.post("/v1/auth/email/request-verification")
    assert res.status == HTTPStatus.UNAUTHORIZED
    assert res.json == UnauthorizedError().to_dict()
