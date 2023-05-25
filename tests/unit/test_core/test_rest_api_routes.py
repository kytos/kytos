"""Test kytos.core.rest_api routes."""
import asyncio
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from kytos.core.auth import UserController
from kytos.core.config import KytosConfig
from kytos.core.rest_api import (JSONResponse, Request, aget_json_or_400,
                                 error_msg, get_body, get_json_or_400)


async def test_new_endpoint(controller, api_client) -> None:
    """Test new core endpoint."""

    def handler(_request: Request) -> JSONResponse:
        return JSONResponse("response")

    endpoint = "prefix/resource"
    controller.api_server.register_core_endpoint(endpoint, handler)
    response = await api_client.get(f"kytos/core/{endpoint}")
    assert response.status_code == 200
    assert response.json() == "response"


async def test_new_async_endpoint(controller, api_client) -> None:
    """Test new core async endpoint."""

    async def handler(_request: Request) -> JSONResponse:
        await asyncio.sleep(0)
        return JSONResponse("response")

    endpoint = "prefix/resource"
    controller.api_server.register_core_endpoint(endpoint, handler)
    response = await api_client.get(f"kytos/core/{endpoint}")
    assert response.status_code == 200
    assert response.json() == "response"


async def test_aget_json_or_400(controller, api_client) -> None:
    """Test aget_json_or_400."""

    async def handler(request: Request) -> JSONResponse:
        body = await aget_json_or_400(request)
        return JSONResponse(body)

    endpoint = "prefix/resource"
    controller.api_server.register_core_endpoint(endpoint, handler,
                                                 methods=["POST"])
    response = await api_client.post(f"kytos/core/{endpoint}")
    assert response.status_code == 400
    body = {"some_key": "some_value"}
    response = await api_client.post(f"kytos/core/{endpoint}", json=body)
    assert response.status_code == 200
    assert response.json() == body


def test_api_500_traceback_by_default() -> None:
    """Test api 500 traceback by default."""
    assert KytosConfig().options["daemon"].api_traceback_on_500


async def test_get_json_or_400(controller, api_client, event_loop) -> None:
    """Test get_json_or_400."""

    controller.loop = event_loop

    def handler(request: Request) -> JSONResponse:
        body = get_json_or_400(request, controller.loop)
        return JSONResponse(body)

    endpoint = "prefix/resource"
    controller.api_server.register_core_endpoint(endpoint, handler,
                                                 methods=["POST"])
    response = await api_client.post(f"kytos/core/{endpoint}")
    assert response.status_code == 400
    body = {"some_key": "some_value"}
    response = await api_client.post(f"kytos/core/{endpoint}", json=body)
    assert response.status_code == 200
    assert response.json() == body


async def test_error_msg():
    """Test error message"""
    user = UserController(MagicMock())
    user_data = {
        "username": "test",
        "password": "password",
        "email": "test@kytos.io"
    }
    with pytest.raises(ValidationError) as err:
        user.create_user(user_data)
    actual_msg = error_msg(err.value.errors())
    expected_msg = 'password: value should contain minimun 8 characters, ' \
                   'at least one upper case character, at least 1 ' \
                   'numeric character [0-9]'
    assert actual_msg == expected_msg


async def test_get_body(controller, api_client, event_loop) -> None:
    """Test get_body (low level-ish usage for validators)."""
    controller.loop = event_loop

    def handler(request: Request) -> JSONResponse:
        body_bytes = get_body(request, controller.loop)
        assert body_bytes == b'{"some_key": "some_value"}'
        return JSONResponse({})

    endpoint = "prefix/resource"
    controller.api_server.register_core_endpoint(endpoint, handler,
                                                 methods=["POST"])
    body = {"some_key": "some_value"}
    response = await api_client.post(f"kytos/core/{endpoint}", json=body)
    assert response.status_code == 200
    assert response.json() == {}
