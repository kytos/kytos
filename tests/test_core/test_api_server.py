"""APIServer tests."""

import unittest

from kytos.core.api_server import APIServer


class TestAPIServer(unittest.TestCase):
    """Test the class APIServer."""

    def setUp(self):
        """Instantiate a APIServer."""
        self.api_server = APIServer('CustomName', False)

    def test_register_rest_endpoint(self):
        """Test whether register_rest_endpoint is registering an endpoint."""
        self.api_server.register_rest_endpoint('/custom_method/',
                                               self.__custom_endpoint,
                                               methods=['GET'])

        expected_endpoint = '/kytos/custom_method/'
        actual_endpoints = self.api_server.rest_endpoints
        self.assertIn(expected_endpoint, actual_endpoints)

    def test_register_api_server_routes(self):
        """Server routes should include status and shutdown endpoints."""
        self.api_server.register_api_server_routes()

        expecteds = ['/kytos/status/', '/kytos/shutdown/',
                     '/static/<path:filename>']

        actual_endpoints = self.api_server.rest_endpoints

        self.assertListEqual(sorted(expecteds), sorted(actual_endpoints))

    def test_rest_endpoints(self):
        """Test whether rest_endpoint returns all registered endpoints."""
        endpoints = ['/custom/', '/custom_2/', '/custom_3/']

        for endpoint in endpoints:
            self.api_server.register_rest_endpoint(endpoint,
                                                   self.__custom_endpoint,
                                                   methods=['GET'])

        expected_endpoints = ['/kytos{}'.format(e) for e in endpoints]
        expected_endpoints.append('/static/<path:filename>')

        actual_endpoints = self.api_server.rest_endpoints
        self.assertListEqual(sorted(expected_endpoints),
                             sorted(actual_endpoints))

    @staticmethod
    def __custom_endpoint():
        """Custom method used by APIServer."""
        return "Custom Endpoint"
