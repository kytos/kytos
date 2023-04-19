"""Unit test fixtures."""
# pylint: disable=redefined-outer-name

import pytest
from httpx import AsyncClient

from kytos.core import Controller
from kytos.core.auth import Auth
from kytos.core.dead_letter import DeadLetter
from kytos.lib.helpers import get_controller_mock


@pytest.fixture
def controller() -> Controller:
    """Controller fixture."""
    yield get_controller_mock()


@pytest.fixture
def dead_letter(controller) -> DeadLetter:
    """DeadLetter fixture."""
    yield controller.dead_letter


@pytest.fixture
def api_client(controller) -> AsyncClient:
    """App test_client instance."""
    base_url = "http://127.0.0.1/api/"
    app = controller.api_server.app
    yield AsyncClient(app=app, base_url=base_url)


@pytest.fixture
def auth(controller) -> Auth:
    """Auth fixture."""
    auth = Auth(controller)
    controller.start_auth()
    yield auth


@pytest.fixture
def minimal_openapi_spec_dict():
    """Sample minimal openapi spec."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Minimal OpenAPI specification", "version": "0.1"},
        "paths": {
            "/status": {
                "get": {
                    "responses": {"default": {"description": "status"}}
                }
            }
        },
    }
