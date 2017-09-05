"""APIServer tests."""

import unittest
from unittest import skip
from unittest.mock import Mock, sentinel

from kytos.core.api_server import APIServer
from kytos.core.napps import rest


class TestAPIServer(unittest.TestCase):
    """Test the class APIServer."""

    def setUp(self):
        """Instantiate a APIServer."""
        self.api_server = APIServer('CustomName', False)

    @skip('Will be renamed to /api/kytos/core/')
    def test_register_rest_endpoint(self):
        """Test whether register_rest_endpoint is registering an endpoint."""
        self.api_server.register_rest_endpoint('/custom_method/',
                                               self.__custom_endpoint,
                                               methods=['GET'])

        expected_endpoint = '/kytos/custom_method/'
        actual_endpoints = self.api_server.rest_endpoints
        self.assertIn(expected_endpoint, actual_endpoints)

    @skip('Will be renamed to /api/kytos/core/')
    def test_register_api_server_routes(self):
        """Server routes should include status and shutdown endpoints."""
        self.api_server.register_api_server_routes()

        expecteds = ['/kytos/status/', '/kytos/shutdown/',
                     '/static/<path:filename>']

        actual_endpoints = self.api_server.rest_endpoints

        self.assertListEqual(sorted(expecteds), sorted(actual_endpoints))

    @skip('Will be renamed to /api/kytos/core/')
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


class TestAPIDecorator(unittest.TestCase):
    """@rest should have the same effect as ``Flask.route``."""

    @classmethod
    def test_flask_call(cls):
        """@rest params should be forwarded to Flask."""
        rule = 'rule'
        # Use sentinels to be sure they are not changed.
        options = dict(param1=sentinel.val1, param2=sentinel.val2)

        class MyNApp:  # pylint: disable=too-few-public-methods
            """API decorator example usage."""

            def __init__(self):
                self.username = 'test'
                self.name = 'MyNApp'

            @rest(rule, **options)
            def my_endpoint(self):
                """Do nothing."""
                pass

        napp = MyNApp()
        server = cls._mock_api_server(napp)
        server.app.add_url_rule.assert_called_once_with(
            '/api/test/MyNApp/' + rule, None, napp.my_endpoint, **options)

    @classmethod
    def test_rule_with_slash(cls):
        """There should be no double slashes in a rule."""
        class MyNApp:  # pylint: disable=too-few-public-methods
            """API decorator example usage."""

            def __init__(self):
                self.username = 'test'
                self.name = 'MyNApp'

            @rest('/rule')
            def my_endpoint(self):
                """Do nothing."""
                pass

        napp = MyNApp()
        server = cls._mock_api_server(napp)
        server.app.add_url_rule.assert_called_once_with(
            '/api/test/MyNApp/rule', None, napp.my_endpoint)

    @staticmethod
    def _mock_api_server(napp):
        """Instantiate APIServer, mock ``.app`` and start ``napp`` API."""
        server = APIServer('test')
        server.app = Mock()  # Flask app
        server.app.url_map.iter_rules.return_value = []

        server.register_napp_endpoints(napp)
        return server
