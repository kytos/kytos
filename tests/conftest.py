"""Unit test fixtures."""
# pylint: disable=redefined-outer-name

from unittest.mock import MagicMock

import pytest

from kytos.core import Controller
from kytos.core.auth import Auth
from kytos.lib.helpers import get_controller_mock


@pytest.fixture(autouse=True)
def ev_loop(monkeypatch, event_loop) -> None:
    """asyncio event loop autouse fixture."""
    monkeypatch.setattr("asyncio.get_running_loop", lambda: event_loop)
    yield event_loop


@pytest.fixture
def controller() -> Controller:
    """Controller fixture."""
    Auth.get_user_controller = MagicMock()
    yield get_controller_mock()


@pytest.fixture
def api_client(controller):
    """Flask app test_client instance."""
    yield controller.api_server.app.test_client()
