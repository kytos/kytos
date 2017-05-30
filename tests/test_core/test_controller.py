"""Controller tests."""

import json
import unittest

from kytos.core.controller import Controller


class TestController(unittest.TestCase):
    """Test the class Controller."""

    def setUp(self):
        """Instantiate a controller with custom options."""
        class CustomOption:
            """Class to represent a custom option used by Kytos."""

            def __init__(self, **kwargs):
                """Construtor method of CustomOption."""
                self.__dict__.update(kwargs)

        options_dict = {'api_port': '8181',
                        'conf': '/etc/kytos/kytos.conf',
                        'daemon': 'False',
                        'debug': 'False',
                        'foreground': True,
                        'installed_napps': '/var/lib/kytos/napps/.installed',
                        'listen': '0.0.0.0',
                        'logging': '/etc/kytos/logging.ini',
                        'napps': '/var/lib/kytos/napps',
                        'napps_repositories': ['https://www.sample.com/repo/'],
                        'pidfile': '/var/run/kytos/kytosd.pid',
                        'port': '6633',
                        'workdir': '/var/lib/kytos'}

        self.options = options_dict
        self.controller = Controller(CustomOption(**options_dict))

    def test_configuration_endpoint(self):
        """Should return the attribute options as json."""
        expected = json.dumps(self.options)
        actual = self.controller.configuration_endpoint()
        self.assertEqual(expected, actual)

    def test_register_configuration_endpoint(self):
        """Should register the endpoint '/kytos/config/'."""
        expected_endpoint = '/kytos/config/'
        actual_endpoints = self.controller.api_server.rest_endpoints
        self.assertIn(expected_endpoint, actual_endpoints)

    def test_register_kytos_endpoints(self):
        """Verify all endpoints registered by Controller."""
        expected_endpoints = ['/kytos/config/', '/kytos/shutdown/',
                              '/kytos/status/', '/index.html', '/',
                              '/static/<path:filename>']
        actual_endpoints = self.controller.api_server.rest_endpoints
        self.assertListEqual(sorted(expected_endpoints),
                             sorted(actual_endpoints))
