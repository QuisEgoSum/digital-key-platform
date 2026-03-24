from http import HTTPStatus

from context.user.application.enums.user_action_token import (
    UserActionTokenKind,
    UserActionTokenStatusType,
)
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.errors.user_email import UserEmailNotFoundError
from fixtures.config import AppConfigPatch
from fixtures.infra.audit import AuditEventQuery
from fixtures.sanic_types import AppSanicTestClient
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
from utils.audit_asserts import audit_event_asserts
from utils.cookie import parse_set_cookie_headers_by_name


async def test_request_password_reset_success(
    sanic_user_http_client: AppSanicTestClient,
    user_action_token_query: UserActionTokenQuery,
    user_factory: UserFactory,
    user_email_agent_mock: UserEmailAgentMock,
    audit_event_query: AuditEventQuery,
) -> None:
    created_user = await user_factory.create()
    user_id = created_user.user.id

    req, res = await sanic_user_http_client.post(
        "/v1/auth/password/request-reset",
        json={"email": created_user.email.email},
    )

    assert res.status_code == HTTPStatus.NO_CONTENT

    assert req.ctx.flow_session is not None
    assert req.ctx.flow_session.kind == UserFlowSessionKind.PASSWORD_RESET

    flow_session_id = req.ctx.flow_session.session_id

    cookies = parse_set_cookie_headers_by_name(res.headers.get_list("set-cookie"))

    assert len(cookies) == 1
    assert cookies["rp_session"].is_deleted is False

    action_tokens = await user_action_token_query.all()

    assert len(action_tokens) == 1

    action_token = action_tokens[0]

    assert action_token.user_id == user_id
    assert action_token.channel_id == created_user.email.id
    assert action_token.status == UserActionTokenStatusType.ACTIVE
    assert action_token.kind == UserActionTokenKind.PASSWORD_RESET

    user_email_agent_mock.send_user_password_reset_email.assert_called_once()

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    audit_event = audit_events[0]

    audit_event_asserts(
        audit_event,
        actor_type=AuditActorType.ANONYMOUS,
        subject_type=AuditSubjectType.USER,
        subject_id=user_id,
        scope_type=AuditScopeType.USER,
        scope_id=user_id,
        action=AuditActionType.PASSWORD_RESET_REQUEST,
        result=AuditResultType.SUCCESS,
        details={
            "outcome": "request_accepted",
            "email": created_user.email.email,
        },
        entities=[
            {
                "type": AuditEntityType.USER_EMAIL,
                "id": created_user.email.id,
                "role": AuditEventEntityRoleType.RELATED,
                "extra": None,
            },
            {
                "type": AuditEntityType.USER_ACTION_TOKEN,
                "id": action_token.id,
                "role": AuditEventEntityRoleType.RESULT,
                "extra": None,
            },
            {
                "type": AuditEntityType.USER_FLOW_SESSION,
                "id": str(flow_session_id),
                "role": AuditEventEntityRoleType.RELATED,
                "extra": {"kind": UserFlowSessionKind.PASSWORD_RESET},
            },
        ],
    )


async def test_request_password_reset_with_not_found(
    sanic_user_http_client: AppSanicTestClient,
    audit_event_query: AuditEventQuery,
) -> None:
    req, res = await sanic_user_http_client.post(
        "/v1/auth/password/request-reset",
        json={"email": "user@example.com"},
    )

    assert res.status_code == HTTPStatus.NO_CONTENT

    assert req.ctx.flow_session is not None
    assert req.ctx.flow_session.user_id is None
    assert req.ctx.flow_session.kind == UserFlowSessionKind.PASSWORD_RESET

    flow_session_id = req.ctx.flow_session.session_id

    cookies = parse_set_cookie_headers_by_name(res.headers.get_list("set-cookie"))

    assert len(cookies) == 1
    assert cookies["rp_session"].is_deleted is False

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    audit_event = audit_events[0]

    audit_event_asserts(
        audit_event,
        actor_type=AuditActorType.ANONYMOUS,
        action=AuditActionType.PASSWORD_RESET_REQUEST,
        result=AuditResultType.REJECTED,
        details={
            "outcome": "user_not_found",
            "email": "user@example.com",
            "error_code": UserEmailNotFoundError.code,
        },
        entities=[
            {
                "type": AuditEntityType.USER_FLOW_SESSION,
                "id": str(flow_session_id),
                "role": AuditEventEntityRoleType.FLOW,
                "extra": {"kind": UserFlowSessionKind.PASSWORD_RESET},
            },
        ],
    )


async def test_request_password_reset_with_not_found_hidden_disabled(
    sanic_user_http_client: AppSanicTestClient,
    audit_event_query: AuditEventQuery,
    app_config_patch: AppConfigPatch,
) -> None:
    app_config_patch.replace_config(
        {
            (
                "context",
                "user",
                "password_reset",
                "hide_email_existence_on_request",
            ): False,
        },
    )

    req, res = await sanic_user_http_client.post(
        "/v1/auth/password/request-reset",
        json={"email": "user@example.com"},
    )

    assert res.status_code == HTTPStatus.NOT_FOUND
    assert res.json == UserEmailNotFoundError().to_dict()

    assert req.ctx.flow_session is None

    cookies = parse_set_cookie_headers_by_name(res.headers.get_list("set-cookie"))

    assert len(cookies) == 0

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    audit_event = audit_events[0]

    audit_event_asserts(
        audit_event,
        actor_type=AuditActorType.ANONYMOUS,
        action=AuditActionType.PASSWORD_RESET_REQUEST,
        result=AuditResultType.REJECTED,
        details={
            "outcome": "user_not_found",
            "email": "user@example.com",
            "error_code": UserEmailNotFoundError.code,
        },
    )
