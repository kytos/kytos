"""Test kytos.core.controller module."""
import json
import logging
from copy import copy
from unittest import TestCase
from unittest.mock import Mock, patch

from kytos.core import Controller
from kytos.core.config import KytosConfig


class TestController(TestCase):
    """Controller tests."""

    def setUp(self):
        """Instantiate a controller."""
        self.options = KytosConfig().options['daemon']
        self.controller = Controller(self.options)

    def test_configuration_endpoint(self):
        """Should return the attribute options as json."""
        serializable_options = vars(self.options)
        expected = json.dumps(serializable_options)
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

    @staticmethod
    @patch('kytos.core.controller.LogManager')
    @patch('kytos.core.logs.Path')
    def test_websocket_log_should_be_enabled(Path, LogManager):
        """Assert that the web socket log is used."""
        # Save original state
        handlers_bak = copy(logging.root.handlers)

        # Minimum to instantiate Controller
        options = Mock(napps='')
        Path.return_value.exists.return_value = False
        controller = Controller(options)

        # The test
        controller.enable_logs()
        LogManager.enable_websocket.assert_called_once()

        # Restore original state
        logging.root.handlers = handlers_bak
