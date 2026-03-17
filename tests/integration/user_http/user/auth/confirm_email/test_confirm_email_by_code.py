from http import HTTPStatus

from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.errors.user_action_token import (
    InvalidUserActionTokenError,
)
from context.user.application.services import user_flow_session_service
from fixtures.infra.audit import AuditEventQuery
from fixtures.sanic_types import AppSanicTestClient
from fixtures.user.auth import UserAuthFactory
from fixtures.user.user import UserFactory
from fixtures.user.user_email import UserEmailQuery
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


async def test_confirm_email_by_code_success(
    sanic_user_http_client: AppSanicTestClient,
    user_factory: UserFactory,
    user_auth_factory: UserAuthFactory,
    user_email_query: UserEmailQuery,
    audit_event_query: AuditEventQuery,
) -> None:
    user = await user_factory.create(verify_email=False)
    verify_flow = await user_auth_factory.create_email_verification_flow(
        user_id=user.user.id,
        email_id=user.email.id,
    )

    sanic_user_http_client.cookies["ev_session"] = verify_flow.flow_session.session_key

    _, res = await sanic_user_http_client.post(
        "/v1/auth/email/verify",
        json={"token": verify_flow.action_token_generated.short_token},
    )

    assert res.status_code == HTTPStatus.NO_CONTENT

    emails = await user_email_query.get_by_user_id(user.user.id)

    assert len(emails) == 1
    assert emails[0].verified_at is not None

    cookies = parse_set_cookie_headers_by_name(res.headers.get_list("set-cookie"))

    assert len(cookies) == 1
    assert cookies["ev_session"].is_deleted is True

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    event = audit_events[0]

    audit_event_asserts(
        event,
        actor_type=AuditActorType.USER,
        actor_key=user.user.id,
        subject_type=AuditSubjectType.USER_EMAIL,
        subject_id=user.email.id,
        scope_type=AuditScopeType.USER,
        scope_id=user.user.id,
        action=AuditActionType.EMAIL_VERIFICATION_CONFIRM,
        result=AuditResultType.SUCCESS,
        details={
            "outcome": "email_verified",
            "flow": "code",
        },
        entities=[
            {
                "type": AuditEntityType.USER_ACTION_TOKEN,
                "id": verify_flow.action_token.id,
                "role": AuditEventEntityRoleType.RELATED,
                "extra": None,
            },
            {
                "type": AuditEntityType.USER_FLOW_SESSION,
                "id": str(verify_flow.flow_session.storage.session_id),
                "role": AuditEventEntityRoleType.SOURCE,
                "extra": {"kind": UserFlowSessionKind.EMAIL_VERIFICATION},
            },
        ],
    )


async def test_confirm_email_by_code_invalid_code(
    sanic_user_http_client: AppSanicTestClient,
    user_factory: UserFactory,
    user_auth_factory: UserAuthFactory,
    audit_event_query: AuditEventQuery,
) -> None:
    user = await user_factory.create(verify_email=False)
    verify_flow = await user_auth_factory.create_email_verification_flow(
        user_id=user.user.id,
        email_id=user.email.id,
    )

    sanic_user_http_client.cookies["ev_session"] = verify_flow.flow_session.session_key

    _, res = await sanic_user_http_client.post(
        "/v1/auth/email/verify",
        json={"token": verify_flow.action_token_generated.short_token + "00"},
    )

    assert res.status_code == HTTPStatus.BAD_REQUEST
    assert res.json == InvalidUserActionTokenError("token_not_found").to_dict()

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    event = audit_events[0]

    audit_event_asserts(
        event,
        actor_type=AuditActorType.USER,
        actor_key=user.user.id,
        subject_type=AuditSubjectType.USER_EMAIL,
        subject_id=user.email.id,
        scope_type=AuditScopeType.USER,
        scope_id=user.user.id,
        action=AuditActionType.EMAIL_VERIFICATION_CONFIRM,
        result=AuditResultType.REJECTED,
        details={
            "outcome": "token_mismatch",
            "flow": "code",
            "error_code": InvalidUserActionTokenError.code,
        },
        entities=[
            {
                "type": AuditEntityType.USER_FLOW_SESSION,
                "id": str(verify_flow.flow_session.storage.session_id),
                "role": AuditEventEntityRoleType.SOURCE,
                "extra": {"kind": UserFlowSessionKind.EMAIL_VERIFICATION},
            },
            {
                "type": AuditEntityType.USER_ACTION_TOKEN,
                "id": verify_flow.action_token.id,
                "role": AuditEventEntityRoleType.RELATED,
                "extra": None,
            },
        ],
    )


async def test_confirm_email_by_code_suppress(
    sanic_user_http_client: AppSanicTestClient,
    audit_event_query: AuditEventQuery,
) -> None:
    flow_session = await user_flow_session_service.create_flow_session(
        user_id=None,
        kind=UserFlowSessionKind.EMAIL_VERIFICATION,
    )

    sanic_user_http_client.cookies["ev_session"] = flow_session.session_key

    _, res = await sanic_user_http_client.post(
        "/v1/auth/email/verify",
        json={"token": "000000"},
    )

    assert res.status_code == HTTPStatus.BAD_REQUEST
    assert res.json == InvalidUserActionTokenError("flow_session_not_bound").to_dict()

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    event = audit_events[0]

    audit_event_asserts(
        event,
        actor_type=AuditActorType.ANONYMOUS,
        action=AuditActionType.EMAIL_VERIFICATION_CONFIRM,
        result=AuditResultType.FAILURE,
        details={
            "outcome": "flow_session_not_bound",
            "flow": "code",
            "error_code": InvalidUserActionTokenError.code,
        },
        entities=[
            {
                "type": AuditEntityType.USER_FLOW_SESSION,
                "id": str(flow_session.storage.session_id),
                "role": AuditEventEntityRoleType.SOURCE,
                "extra": {"kind": UserFlowSessionKind.EMAIL_VERIFICATION},
            },
        ],
    )
