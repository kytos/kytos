"""Test kytos.core.rest_api routes."""
import asyncio

from kytos.core.rest_api import JSONResponse, Request, aget_json_or_400, get_json_or_400

# TODO test other methods


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


async def test_get_json_or_400(controller, api_client) -> None:
    """Test get_json_or_400."""

    def handler(request: Request) -> JSONResponse:
        body = get_json_or_400(request)
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
