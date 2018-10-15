"""Test kytos.core.controller module."""
import asyncio
import json
import logging
import warnings
from copy import copy
from unittest import TestCase
from unittest.mock import Mock, patch

from kytos.core import Controller
from kytos.core.config import KytosConfig


class TestController(TestCase):
    """Controller tests."""

    def setUp(self):
        """Instantiate a controller."""

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        self.options = KytosConfig().options['daemon']
        self.controller = Controller(self.options, loop=self.loop)
        self.controller.log = Mock()

    def test_configuration_endpoint(self):
        """Should return the attribute options as json."""
        serializable_options = vars(self.options)
        expected = json.dumps(serializable_options)
        actual = self.controller.configuration_endpoint()
        self.assertEqual(expected, actual)

    @staticmethod
    @patch('kytos.core.controller.LogManager')
    @patch('kytos.core.logs.Path')
    def test_websocket_log_usage(path, log_manager):
        """Assert that the web socket log is used."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        # Save original state
        handlers_bak = copy(logging.root.handlers)

        # Minimum to instantiate Controller
        options = Mock(napps='')
        path.return_value.exists.return_value = False
        controller = Controller(options, loop=loop)

        # The test
        controller.enable_logs()
        log_manager.enable_websocket.assert_called_once()

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

    def test_deprecation_warning(self):
        """Deprecated method should suggest @rest decorator."""
        with warnings.catch_warnings(record=True) as wrngs:
            warnings.simplefilter("always")  # trigger all warnings
            self.controller.register_rest_endpoint('x', lambda x: x, ['GET'])
            self.assertEqual(1, len(wrngs))
            warning = wrngs[0]
            self.assertEqual(warning.category, DeprecationWarning)
            self.assertIn('@rest', str(warning.message))
