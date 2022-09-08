"""Test kytos.core.api_server routes with Flask test_client."""
import asyncio

KYTOS_CORE_API = "http://127.0.0.1:8181/api/kytos/core"


class TestAPIRoutes:
    """TestAPIRoutes."""

    def test_new_endpoint(self, controller, api_client) -> None:
        """Test new core endpoint."""

        def handler():
            return "response", 200

        endpoint = "prefix/resource"
        controller.api_server.register_core_endpoint(endpoint, handler)
        url = f"{KYTOS_CORE_API}/{endpoint}"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.get_data() == b"response"

    def test_new_async_endpoint(self, controller, api_client) -> None:
        """Test new core async endpoint."""

        async def handler():
            await asyncio.sleep(0)
            return "response", 200

        endpoint = "prefix/resource"
        controller.api_server.register_core_endpoint(endpoint, handler)
        url = f"{KYTOS_CORE_API}/{endpoint}"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.get_data() == b"response"
