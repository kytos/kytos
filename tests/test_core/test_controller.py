"""Test kytos.core.controller module."""
import json
import logging
from copy import copy
from unittest import TestCase, skip
from unittest.mock import Mock, patch

from kytos.core import Controller
from kytos.core.config import KytosConfig


class TestController(TestCase):
    """Controller tests."""

    def setUp(self):
        """Instantiate a controller."""
        self.options = KytosConfig().options['daemon']
        self.controller = Controller(self.options)
        self.controller.log = Mock()

    def test_configuration_endpoint(self):
        """Should return the attribute options as json."""
        serializable_options = vars(self.options)
        expected = json.dumps(serializable_options)
        actual = self.controller.configuration_endpoint()
        self.assertEqual(expected, actual)

    @skip('Will be renamed to /api/kytos/core/')
    def test_register_configuration_endpoint(self):
        """Should register the endpoint '/kytos/config/'."""
        expected_endpoint = '/kytos/config/'
        actual_endpoints = self.controller.api_server.rest_endpoints
        self.assertIn(expected_endpoint, actual_endpoints)

    @skip('Will be renamed to /api/kytos/core/')
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

    def test_unload_napp_listener(self):
        """Call NApp shutdown listener on unload."""
        username, napp_name = 'test', 'napp'
        listener = self._add_napp(username, napp_name)

        listener.assert_not_called()
        self.controller.unload_napp(username, napp_name)
        listener.assert_called()

    def test_unload_napp_other_listener(self):
        """Should not call other NApps' shutdown listener on unload."""
        username, napp_name = 'test', 'napp1'
        self._add_napp(username, napp_name)
        other_listener = self._add_napp('test', 'napp2')

        self.controller.unload_napp(username, napp_name)
        other_listener.assert_not_called()

    def _add_napp(self, username, napp_name):
        """Add a mocked NApp to the controller."""
        napp_id = f'{username}/{napp_name}'
        event_name = f'kytos/core.shutdown.{napp_id}'
        listener = Mock()
        self.controller.events_listeners[event_name] = [listener]
        napp = Mock(_listeners={})
        self.controller.napps[(username, napp_name)] = napp
        return listener
