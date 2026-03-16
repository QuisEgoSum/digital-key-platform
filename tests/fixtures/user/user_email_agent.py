from unittest.mock import AsyncMock

import pytest

from _pytest.monkeypatch import MonkeyPatch

from context.user.infra.gateways.email import user_email_agent


@pytest.fixture()
async def mock_send_email_verification_email(monkeypatch: MonkeyPatch) -> AsyncMock:
    mock = AsyncMock()

    monkeypatch.setattr(
        user_email_agent,
        "send_email_verification_email",
        mock,
    )

    return mock


@pytest.fixture()
async def mock_send_user_password_reset_email(monkeypatch: MonkeyPatch) -> AsyncMock:
    mock = AsyncMock()

    monkeypatch.setattr(
        user_email_agent,
        "send_user_password_reset_email",
        mock,
    )

    return mock
