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
from kytos.core.logs import LogManager


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

    def test_loggers(self):
        """Test that all controller loggers are under kytos
        hierarchy logger.
        """
        loggers = self.controller.loggers()
        for logger in loggers:
            self.assertTrue(logger.name.startswith("kytos"))

    def test_debug_on(self):
        """Test the enable debug feature."""
        # Enable debug for kytos.core
        self.controller.toggle_debug("kytos.core")
        self._test_debug_result()

    def test_debug_on_defaults(self):
        """Test the enable debug feature. Test the default parameter"""
        # Enable debug for kytos.core
        self.controller.toggle_debug("kytos.core")
        self._test_debug_result()

    def _test_debug_result(self):
        """Verify if the loggers have level debug."""
        loggers = self.controller.loggers()
        for logger in loggers:
            # Check if all kytos.core loggers are in DEBUG mode.
            # All the rest must remain the same.
            if logger.name.startswith("kytos.core"):
                self.assertTrue(logger.getEffectiveLevel(), logging.DEBUG)
            else:
                self.assertTrue(logger.getEffectiveLevel(), logging.CRITICAL)

    def test_debug_off(self):
        """Test the disable debug feature"""
        # Fist we enable the debug
        self.controller.toggle_debug("kytos.core")
        # ... then we disable the debug for the test
        self.controller.toggle_debug("kytos.core")
        loggers = self.controller.loggers()
        for logger in loggers:
            self.assertTrue(logger.getEffectiveLevel(), logging.CRITICAL)

    @patch.object(LogManager, 'load_config_file')
    def test_debug_no_name(self, mock_load_config_file):
        """Test the enable debug logger with default levels."""
        # Mock the LogManager that loads the default Loggers
        self.controller.toggle_debug()
        self._test_debug_result()

        mock_load_config_file.assert_called_once()

    @patch.object(LogManager, 'load_config_file')
    def test_debug_empty_name(self, mock_load_config_file):
        """Test the enable debug logger with default levels."""
        # Mock the LogManager that loads the default Loggers
        self.controller.toggle_debug('')
        self._test_debug_result()

        mock_load_config_file.assert_called_once()

    def test_debug_wrong_name(self):
        """Test the enable debug logger with wrong name."""
        self.assertRaises(ValueError,
                          self.controller.toggle_debug, name="foobar")
