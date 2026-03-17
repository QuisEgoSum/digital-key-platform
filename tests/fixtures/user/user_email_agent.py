from dataclasses import dataclass
from unittest.mock import AsyncMock

import pytest

from _pytest.monkeypatch import MonkeyPatch

from context.user.infra.gateways.email import user_email_agent


@dataclass()
class UserEmailAgentMock:
    send_email_verification_email: AsyncMock
    send_user_password_reset_email: AsyncMock


@pytest.fixture()
def user_email_agent_mock(monkeypatch: MonkeyPatch) -> UserEmailAgentMock:
    mock = UserEmailAgentMock(
        send_email_verification_email=AsyncMock(),
        send_user_password_reset_email=AsyncMock(),
    )

    monkeypatch.setattr(
        user_email_agent,
        "send_email_verification_email",
        mock.send_email_verification_email,
    )
    monkeypatch.setattr(
        user_email_agent,
        "send_user_password_reset_email",
        mock.send_user_password_reset_email,
    )

    return mock
