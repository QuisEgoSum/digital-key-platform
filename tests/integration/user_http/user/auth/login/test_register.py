from http import HTTPStatus
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from context.user.application.enums.user import UserStatus
from context.user.application.enums.user_action_token import (
    UserActionTokenKind,
    UserActionTokenStatusType,
)
from context.user.application.enums.user_flow_session import UserFlowSessionKind
from fixtures.infra.audit import GetAuditEventsFactory
from fixtures.sanic_types import AppSanicTestClient
from fixtures.user.user import GetUsersFactory
from fixtures.user.user_action_token import GetUserActionTokensFactory
from fixtures.user.user_credentials import GetUserCredentialsByUserIDFactory
from fixtures.user.user_email import GetUserEmailsByUserIdFactory
from infra.audit.enums import (
    AuditActionType,
    AuditActorType,
    AuditEntityType,
    AuditEventEntityRoleType,
    AuditResultType,
    AuditScopeType,
    AuditSubjectType,
)
from shared.security.hash import verify_password
from utils.audit_asserts import audit_event_asserts
from utils.cookie import parse_set_cookie_headers_by_name

if TYPE_CHECKING:
    from context.user.infra.models import UserRow


async def test_register_success(
    sanic_user_http_client: AppSanicTestClient,
    get_users_factory: GetUsersFactory,
    get_user_action_tokens_factory: GetUserActionTokensFactory,
    get_user_credentials_by_user_id_factory: GetUserCredentialsByUserIDFactory,
    get_user_emails_by_user_id_factory: GetUserEmailsByUserIdFactory,
    mock_send_email_verification_email: AsyncMock,
    get_audit_events_factory: GetAuditEventsFactory,
) -> None:
    req, res = await sanic_user_http_client.post(
        "/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "password",
            "name": "User",
            "locale": "en",
            "timezone": "UTC",
        },
    )

    assert res.status_code == HTTPStatus.CREATED
    assert res.json == {"status": "email_verification_required"}

    users = await get_users_factory()

    assert len(users) == 1

    user: UserRow = users[0]

    assert user.name == "User"
    assert user.status == UserStatus.ACTIVE
    assert user.status_until_at is None
    assert user.locale == "en"
    assert user.timezone == "UTC"

    emails = await get_user_emails_by_user_id_factory(user.id)

    assert len(emails) == 1

    user_email = emails[0]

    assert user_email.email == "user@example.com"
    assert user_email.is_primary is True
    assert user_email.verified_at is None
    assert user_email.revoked_at is None

    credentials = await get_user_credentials_by_user_id_factory(user.id)

    assert credentials.password_hash is not None
    assert credentials.password_hash != "password"
    assert verify_password(
        plain_password="password",
        hashed_password=credentials.password_hash,
    )
    assert credentials.password_changed_at is None

    user_action_tokens = await get_user_action_tokens_factory()

    assert len(user_action_tokens) == 1

    ev_token = user_action_tokens[0]

    assert ev_token.user_id == user.id
    assert ev_token.kind == UserActionTokenKind.EMAIL_VERIFICATION
    assert ev_token.status == UserActionTokenStatusType.ACTIVE

    flow_session = req.ctx.flow_session

    assert flow_session is not None
    assert flow_session.kind == UserFlowSessionKind.EMAIL_VERIFICATION
    assert flow_session.user_id == user.id

    cookies = parse_set_cookie_headers_by_name(res.headers.get_list("set-cookie"))

    assert len(cookies) == 1
    assert "ev_session" in cookies

    ev_cookie = cookies["ev_session"]

    assert ev_cookie.value.startswith(str(flow_session.session_id))
    assert ev_cookie.is_deleted is False

    mock_send_email_verification_email.assert_called_once()
    mock_send_email_verification_email.assert_called_once()
    _, kwargs = mock_send_email_verification_email.call_args

    assert kwargs["user_email"].id == user_email.id
    assert kwargs["action_token"].id == ev_token.id

    audit_events = await get_audit_events_factory()

    assert len(audit_events) == 2

    register_event = audit_events[0]
    email_event = audit_events[1]

    audit_event_asserts(
        register_event,
        actor_type=AuditActorType.ANONYMOUS,
        subject_type=AuditSubjectType.USER,
        subject_id=user.id,
        subject_extra={"email": "user@example.com"},
        scope_type=AuditScopeType.USER,
        scope_id=user.id,
        action=AuditActionType.REGISTER,
        result=AuditResultType.SUCCESS,
    )
    audit_event_asserts(
        email_event,
        actor_type=AuditActorType.USER,
        actor_key=user.id,
        subject_type=AuditSubjectType.USER_EMAIL,
        subject_id=user_email.id,
        scope_type=AuditScopeType.USER,
        scope_id=user.id,
        action=AuditActionType.EMAIL_VERIFICATION_REQUEST,
        result=AuditResultType.SUCCESS,
        outcome="request_accepted",
        entities=[
            {
                "type": AuditEntityType.USER_ACTION_TOKEN,
                "id": ev_token.id,
                "role": AuditEventEntityRoleType.RESULT,
                "extra": None,
            },
            {
                "type": AuditEntityType.USER_FLOW_SESSION,
                "id": str(flow_session.session_id),
                "role": AuditEventEntityRoleType.FLOW,
                "extra": {"kind": UserFlowSessionKind.EMAIL_VERIFICATION},
            },
        ],
    )


async def test_register_duplicate(
    sanic_user_http_client: AppSanicTestClient,
    get_audit_events_factory: GetAuditEventsFactory,
) -> None:
    payload = {
        "email": "user@example.com",
        "password": "password",
        "name": "User",
    }

    req, res = await sanic_user_http_client.post(
        "/v1/auth/register",
        json=payload,
    )

    assert res.status_code == HTTPStatus.CREATED
    assert res.json == {"status": "email_verification_required"}

    req, res = await sanic_user_http_client.post(
        "/v1/auth/register",
        json=payload,
    )

    assert res.status_code == HTTPStatus.CREATED
    assert res.json == {"status": "email_verification_required"}

    flow_session = req.ctx.flow_session

    assert flow_session is not None
    assert flow_session.kind == UserFlowSessionKind.EMAIL_VERIFICATION
    assert flow_session.user_id is None

    cookies = parse_set_cookie_headers_by_name(res.headers.get_list("set-cookie"))

    assert len(cookies) == 1
    assert "ev_session" in cookies

    ev_cookie = cookies["ev_session"]

    assert ev_cookie.is_deleted is False
    assert ev_cookie.value is not None
    assert ev_cookie.value.startswith(str(flow_session.session_id))

    audit_events = await get_audit_events_factory()

    assert len(audit_events) == 3

    register_event = audit_events[2]

    audit_event_asserts(
        register_event,
        actor_type=AuditActorType.ANONYMOUS,
        subject_type=AuditSubjectType.USER,
        subject_extra={"email": "user@example.com"},
        action=AuditActionType.REGISTER,
        result=AuditResultType.REJECTED,
        outcome="email_already_exists",
        entities=[
            {
                "type": AuditEntityType.USER_FLOW_SESSION,
                "id": str(flow_session.session_id),
                "role": AuditEventEntityRoleType.FLOW,
                "extra": {"kind": flow_session.kind},
            },
        ],
    )
