from http import HTTPStatus

from context.user.application.enums.user_flow_session import UserFlowSessionKind
from context.user.application.errors.auth import InvalidCredentialsError
from fixtures.infra.audit import AuditEventQuery
from fixtures.sanic_types import AppSanicTestClient
from fixtures.user.user import UserFactory
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


async def test_login_success(
    sanic_user_http_client: AppSanicTestClient,
    user_factory: UserFactory,
    audit_event_query: AuditEventQuery,
) -> None:
    created_user = await user_factory.create()
    user_id = created_user.user.id

    req, res = await sanic_user_http_client.post(
        "/v1/auth/login",
        json={
            "email": created_user.email.email,
            "password": "password",
        },
    )

    assert res.status_code == HTTPStatus.OK
    assert res.json["status"] == "logged_in"
    assert res.json["user"] is not None
    assert res.json["user"]["id"] == created_user.user.id

    cookies = parse_set_cookie_headers_by_name(res.headers.get_list("set-cookie"))

    assert len(cookies) == 1
    assert cookies["session"].is_deleted is False

    assert req.ctx.session is not None

    session_id = req.ctx.session.session_id

    assert cookies["session"].value is not None
    assert cookies["session"].value.startswith(str(session_id))

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    event = audit_events[0]

    audit_event_asserts(
        event,
        actor_type=AuditActorType.USER,
        actor_key=user_id,
        subject_type=AuditSubjectType.USER,
        subject_id=user_id,
        scope_type=AuditScopeType.USER,
        scope_id=user_id,
        action=AuditActionType.LOGIN,
        result=AuditResultType.SUCCESS,
        details={
            "outcome": "logged_in",
        },
        entities=[
            {
                "type": AuditEntityType.USER_SESSION,
                "id": str(session_id),
                "role": AuditEventEntityRoleType.RESULT,
                "extra": None,
            },
        ],
    )


async def test_login_not_verified_email(
    sanic_user_http_client: AppSanicTestClient,
    user_factory: UserFactory,
    audit_event_query: AuditEventQuery,
) -> None:
    created_user = await user_factory.create(verify_email=False)
    user_id = created_user.user.id

    req, res = await sanic_user_http_client.post(
        "/v1/auth/login",
        json={
            "email": created_user.email.email,
            "password": "password",
        },
    )

    assert res.status_code == HTTPStatus.OK
    assert res.json["status"] == "email_verification_required"
    assert "user" not in res.json

    cookies = parse_set_cookie_headers_by_name(res.headers.get_list("set-cookie"))

    assert len(cookies) == 1
    assert cookies["ev_session"].is_deleted is False

    assert req.ctx.session is None
    assert req.ctx.flow_session is not None

    flow_session_id = req.ctx.flow_session.session_id

    assert cookies["ev_session"].value is not None
    assert cookies["ev_session"].value.startswith(str(flow_session_id))

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    event = audit_events[0]

    audit_event_asserts(
        event,
        actor_type=AuditActorType.USER,
        actor_key=user_id,
        subject_type=AuditSubjectType.USER,
        subject_id=user_id,
        scope_type=AuditScopeType.USER,
        scope_id=user_id,
        action=AuditActionType.LOGIN,
        result=AuditResultType.SUCCESS,
        details={
            "outcome": "email_verification_required",
        },
        entities=[
            {
                "type": AuditEntityType.USER_FLOW_SESSION,
                "id": str(flow_session_id),
                "role": AuditEventEntityRoleType.RESULT,
                "extra": {"kind": UserFlowSessionKind.EMAIL_VERIFICATION},
            },
        ],
    )


async def test_login_invalid_credentials(
    sanic_user_http_client: AppSanicTestClient,
    user_factory: UserFactory,
    audit_event_query: AuditEventQuery,
) -> None:
    created_user = await user_factory.create()
    user_id = created_user.user.id

    _, res = await sanic_user_http_client.post(
        "/v1/auth/login",
        json={
            "email": created_user.email.email,
            "password": "invalid password",
        },
    )

    assert res.status_code == HTTPStatus.UNAUTHORIZED
    assert res.json == InvalidCredentialsError("invalid_password").to_dict()

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    event = audit_events[0]

    audit_event_asserts(
        event,
        actor_type=AuditActorType.USER,
        actor_key=user_id,
        subject_type=AuditSubjectType.USER,
        subject_id=user_id,
        scope_type=AuditScopeType.USER,
        scope_id=user_id,
        action=AuditActionType.LOGIN,
        result=AuditResultType.FAILURE,
        details={
            "outcome": "invalid_password",
            "error_code": InvalidCredentialsError.code,
        },
    )


async def test_login_user_not_found(
    sanic_user_http_client: AppSanicTestClient,
    audit_event_query: AuditEventQuery,
) -> None:
    _, res = await sanic_user_http_client.post(
        "/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "password",
        },
    )

    assert res.status_code == HTTPStatus.UNAUTHORIZED
    assert res.json == InvalidCredentialsError("user_not_found").to_dict()

    audit_events = await audit_event_query.all()

    assert len(audit_events) == 1

    event = audit_events[0]

    audit_event_asserts(
        event,
        actor_type=AuditActorType.ANONYMOUS,
        subject_type=AuditSubjectType.USER,
        subject_extra={"email": "user@example.com"},
        action=AuditActionType.LOGIN,
        result=AuditResultType.FAILURE,
        details={
            "outcome": "user_not_found",
            "error_code": InvalidCredentialsError.code,
        },
    )
