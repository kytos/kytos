"""Test kytos.core.controller module."""
import asyncio
import json
import logging
import warnings
from copy import copy
from unittest import TestCase
from unittest.mock import MagicMock, Mock, call, patch

from kytos.core import Controller
from kytos.core.config import KytosConfig
from kytos.core.logs import LogManager


# pylint: disable=too-many-public-methods
class TestController(TestCase):
    """Controller tests."""

    def setUp(self):
        """Instantiate a controller."""

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        self.options = KytosConfig().options['daemon']
        self.napps_manager = Mock()
        self.controller = Controller(self.options, loop=self.loop)
        self.controller.napps_manager = self.napps_manager
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

    def test_get_interface_by_id__not_interface(self):
        """Test get_interface_by_id method when interface does not exist."""
        resp_interface = self.controller.get_interface_by_id(None)

        self.assertIsNone(resp_interface)

    def test_get_interface_by_id__not_switch(self):
        """Test get_interface_by_id method when switch does not exist."""
        interface = MagicMock()
        switch = MagicMock()
        switch.interfaces = {123: interface}
        self.controller.switches = {'00:00:00:00:00:00:00:02': switch}

        interface_id = '00:00:00:00:00:00:00:01:123'
        resp_interface = self.controller.get_interface_by_id(interface_id)

        self.assertIsNone(resp_interface)

    def test_get_interface_by_id(self):
        """Test get_interface_by_id method."""
        interface = MagicMock()
        switch = MagicMock()
        switch.interfaces = {123: interface}
        self.controller.switches = {'00:00:00:00:00:00:00:01': switch}

        interface_id = '00:00:00:00:00:00:00:01:123'
        resp_interface = self.controller.get_interface_by_id(interface_id)

        self.assertEqual(resp_interface, interface)

    def test_get_switch_by_dpid(self):
        """Test get_switch_by_dpid method."""
        dpid = '00:00:00:00:00:00:00:01'
        switch = MagicMock(dpid=dpid)
        self.controller.switches = {dpid: switch}

        resp_switch = self.controller.get_switch_by_dpid(dpid)

        self.assertEqual(resp_switch, switch)

    def test_get_switch_or_create__exists(self):
        """Test status_api method when switch exists."""
        dpid = '00:00:00:00:00:00:00:01'
        switch = MagicMock(dpid=dpid)
        self.controller.switches = {dpid: switch}

        connection = MagicMock()
        resp_switch = self.controller.get_switch_or_create(dpid, connection)

        self.assertEqual(resp_switch, switch)

    def test_get_switch_or_create__not_exists(self):
        """Test status_api method when switch does not exist."""
        self.controller.switches = {}

        dpid = '00:00:00:00:00:00:00:01'
        connection = MagicMock()
        switch = self.controller.get_switch_or_create(dpid, connection)

        expected_switches = {'00:00:00:00:00:00:00:01': switch}
        self.assertEqual(self.controller.switches, expected_switches)

    def test_create_or_update_connection(self):
        """Test create_or_update_connection method."""
        self.controller.connections = {}

        connection = MagicMock()
        connection.id = '123'
        self.controller.create_or_update_connection(connection)

        self.assertEqual(self.controller.connections, {'123': connection})

    def test_get_connection_by_id(self):
        """Test get_connection_by_id method."""
        connection = MagicMock()
        connection.id = '123'
        self.controller.connections = {connection.id: connection}

        resp_connection = self.controller.get_connection_by_id('123')

        self.assertEqual(resp_connection, connection)

    def test_remove_connection(self):
        """Test remove_connection method."""
        connection = MagicMock()
        connection.id = '123'
        self.controller.connections = {connection.id: connection}

        self.controller.remove_connection(connection)

        self.assertEqual(self.controller.connections, {})

    def test_remove_switch(self):
        """Test remove_switch method."""
        switch = MagicMock()
        switch.dpid = '00:00:00:00:00:00:00:01'
        self.controller.switches = {switch.dpid: switch}

        self.controller.remove_switch(switch)

        self.assertEqual(self.controller.switches, {})

    def test_new_connection(self):
        """Test new_connection method."""
        self.controller.connections = {}

        connection = MagicMock()
        connection.id = '123'
        event = MagicMock()
        event.source = connection
        self.controller.new_connection(event)

        self.assertEqual(self.controller.connections, {'123': connection})

    def test_add_new_switch(self):
        """Test add_new_switch method."""
        self.controller.switches = {}

        switch = MagicMock()
        switch.dpid = '00:00:00:00:00:00:00:01'
        self.controller.add_new_switch(switch)

        expected_switches = {'00:00:00:00:00:00:00:01': switch}
        self.assertEqual(self.controller.switches, expected_switches)

    @patch('kytos.core.api_server.APIServer.register_napp_endpoints')
    @patch('kytos.core.controller.Controller._import_napp')
    def test_load_napp(self, *args):
        """Test load_napp method."""
        (mock_import_napp, mock_register) = args
        self.controller.napps = {}

        napp = MagicMock()
        module = MagicMock()
        module.Main.return_value = napp
        mock_import_napp.return_value = module

        self.controller.load_napp('kytos', 'napp')

        self.assertEqual(self.controller.napps, {('kytos', 'napp'): napp})
        napp.start.assert_called()
        mock_register.assert_called_with(napp)

    def test_pre_install_napps(self):
        """Test pre_install_napps method."""
        napp_1 = MagicMock()
        napp_2 = MagicMock()
        installed_napps = [napp_1]
        napps = [str(napp_1), str(napp_2)]
        self.napps_manager.get_installed_napps.return_value = installed_napps

        self.controller.pre_install_napps(napps)

        self.napps_manager.install.assert_called_with(str(napp_2), enable=True)

    @patch('kytos.core.controller.Controller.load_napp')
    def test_load_napps(self, mock_load):
        """Test load_napps method."""
        napp = MagicMock()
        napp.username = 'kytos'
        napp.name = 'name'
        enabled_napps = [napp]
        self.napps_manager.get_enabled_napps.return_value = enabled_napps

        self.controller.load_napps()

        mock_load.assert_called_with('kytos', 'name')

    @patch('kytos.core.controller.reload_module')
    @patch('kytos.core.controller.import_module')
    def test_reload_napp_module(self, *args):
        """Test reload_napp_module method."""
        (mock_import_module, mock_reload_module) = args
        napp_module = MagicMock()
        mock_import_module.return_value = napp_module

        self.controller.reload_napp_module('kytos', 'napp', 'napp_file')

        mock_import_module.assert_called_with('napps.kytos.napp.napp_file')
        mock_reload_module.assert_called_with(napp_module)

    @patch('kytos.core.controller.Controller.load_napp')
    @patch('kytos.core.controller.Controller.unload_napp')
    @patch('kytos.core.controller.Controller.reload_napp_module')
    def test_reload_napp(self, *args):
        """Test reload_napp method."""
        (mock_reload_napp_module, mock_unload, mock_load) = args

        self.controller.reload_napp('kytos', 'napp')

        mock_unload.assert_called_with('kytos', 'napp')
        calls = [call('kytos', 'napp', 'settings'),
                 call('kytos', 'napp', 'main')]
        mock_reload_napp_module.assert_has_calls(calls)
        mock_load.assert_called_with('kytos', 'napp')

    @patch('kytos.core.controller.Controller.reload_napp', return_value=200)
    def test_rest_reload_napp(self, mock_reload_napp):
        """Test rest_reload_napp method."""
        resp, code = self.controller.rest_reload_napp('kytos', 'napp')

        mock_reload_napp.assert_called_with('kytos', 'napp')
        self.assertEqual(resp, 'reloaded')
        self.assertEqual(code, 200)

    @patch('kytos.core.controller.Controller.reload_napp')
    def test_rest_reload_all_napps(self, mock_reload_napp):
        """Test rest_reload_all_napps method."""
        self.controller.napps = [('kytos', 'napp')]
        resp, code = self.controller.rest_reload_all_napps()

        mock_reload_napp.assert_called_with('kytos', 'napp')
        self.assertEqual(resp, 'reloaded')
        self.assertEqual(code, 200)
