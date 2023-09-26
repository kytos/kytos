"""Test kytos.core.controller module."""
import json
import logging
import sys
import tempfile
import warnings
from copy import copy
from unittest import TestCase
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from pyof.foundation.exceptions import PackException

from kytos.core import Controller
from kytos.core.auth import Auth
from kytos.core.buffers import KytosBuffers
from kytos.core.config import KytosConfig
from kytos.core.events import KytosEvent
from kytos.core.exceptions import KytosNAppSetupException
from kytos.core.logs import LogManager
from kytos.core.rest_api import Request


# pylint: disable=protected-access, too-many-public-methods
class TestController(TestCase):
    """Controller tests."""

    def setUp(self):
        """Instantiate a controller."""

        self.options = KytosConfig().options['daemon']
        self.napps_manager = Mock()
        Auth.get_user_controller = MagicMock()
        self.controller = Controller(self.options)
        self.controller._buffers = MagicMock()
        self.controller.napps_manager = self.napps_manager
        self.controller.log = Mock()
        self.controller.log.getEffectiveLevel.return_value = 20
        self.app = self.controller.api_server.app
        self.base_url = "http://127.0.0.1/api/kytos/core/"

    @staticmethod
    @patch('kytos.core.controller.LogManager')
    @patch('kytos.core.logs.Path')
    @pytest.mark.skip(reason="TODO issue 371 in a future PR")
    def test_websocket_log_usage(path, log_manager):
        """Assert that the web socket log is used."""
        # Save original state
        handlers_bak = copy(logging.root.handlers)

        # Minimum to instantiate Controller
        options = Mock(napps='', logger_decorators=[])
        path.return_value.exists.return_value = False
        controller = Controller(options)

        # The test
        controller.enable_logs()
        log_manager.enable_websocket.assert_called_once()

        # Restore original state
        logging.root.handlers = handlers_bak

    @patch('kytos.core.api_server.APIServer.remove_napp_endpoints')
    def test_unload_napp_listener(self, _):
        """Call NApp shutdown listener on unload."""
        username, napp_name = 'test', 'napp'
        listener = self._add_napp(username, napp_name)

        listener.assert_not_called()
        self.controller.unload_napp(username, napp_name)
        listener.assert_called()

    @patch('kytos.core.api_server.APIServer.remove_napp_endpoints')
    def test_unload_napp_other_listener(self, _):
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

    @patch('kytos.core.controller.Controller.init_apm_or_core_shutdown')
    @patch('kytos.core.controller.Controller.db_conn_or_core_shutdown')
    @patch('kytos.core.controller.Controller.start_controller')
    @patch('kytos.core.controller.Controller.create_pidfile')
    @patch('kytos.core.controller.Controller.enable_logs')
    def test_start(self, *args):
        """Test start method."""
        (mock_enable_logs, mock_create_pidfile,
         mock_start_controller, mock_db_conn_or_shutdown,
         mock_init_apm_or_shutdown) = args
        self.controller.start()

        mock_enable_logs.assert_called()
        mock_create_pidfile.assert_called()
        mock_start_controller.assert_called()
        mock_db_conn_or_shutdown.assert_not_called()
        mock_init_apm_or_shutdown.assert_not_called()

    @patch('kytos.core.controller.sys')
    @patch('kytos.core.controller.Controller.init_apm_or_core_shutdown')
    @patch('kytos.core.controller.Controller.db_conn_or_core_shutdown')
    @patch('kytos.core.controller.Controller.start_controller')
    @patch('kytos.core.controller.Controller.create_pidfile')
    @patch('kytos.core.controller.Controller.enable_logs')
    def test_start_error_broad_exception(self, *args):
        """Test start error handling broad exception."""
        (mock_enable_logs, mock_create_pidfile,
         mock_start_controller, mock_db_conn_or_shutdown,
         mock_init_apm_or_shutdown, mock_sys) = args
        mock_start_controller.side_effect = Exception
        self.controller.log = MagicMock()
        self.controller.start()

        mock_enable_logs.assert_called()
        mock_create_pidfile.assert_called()
        mock_start_controller.assert_called()
        mock_db_conn_or_shutdown.assert_not_called()
        mock_init_apm_or_shutdown.assert_not_called()
        self.controller.log.exception.assert_called()
        mock_sys.exit.assert_called()

    @patch('kytos.core.controller.Controller.init_apm_or_core_shutdown')
    @patch('kytos.core.controller.Controller.db_conn_or_core_shutdown')
    @patch('kytos.core.controller.Controller.start_controller')
    @patch('kytos.core.controller.Controller.create_pidfile')
    @patch('kytos.core.controller.Controller.enable_logs')
    def test_start_with_mongodb_and_apm(self, *args):
        """Test start method with database and APM options set."""
        (mock_enable_logs, mock_create_pidfile,
         mock_start_controller, mock_db_conn_or_shutdown,
         mock_init_apm_or_shutdown) = args
        self.controller.options.database = "mongodb"
        self.controller.options.apm = "es"
        self.controller.start()

        mock_enable_logs.assert_called()
        mock_create_pidfile.assert_called()
        mock_start_controller.assert_called()
        mock_db_conn_or_shutdown.assert_called()
        mock_init_apm_or_shutdown.assert_called()

    @patch('kytos.core.controller.sys.exit')
    @patch('kytos.core.controller.Controller.start_controller')
    @patch('kytos.core.controller.Controller.create_pidfile')
    @patch('kytos.core.controller.Controller.enable_logs')
    def test_start_with_invalid_database_backend(self, *args):
        """Test start method with unsupported database backend."""
        (mock_enable_logs, _,
         mock_start_controller, mock_sys_exit) = args
        self.controller.options.database = "invalid"
        self.controller.start()
        mock_enable_logs.assert_called()
        mock_start_controller.assert_called()
        mock_sys_exit.assert_called()

    @patch('os.getpid')
    @patch('kytos.core.controller.atexit')
    def test_create_pidfile(self, *args):
        """Test activate method."""
        (_, mock_getpid) = args
        mock_getpid.return_value = 2
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(b'4194305')  # pid_max +1
            tmp_file.seek(0)
            self.controller.options.pidfile = tmp_file.name

            self.controller.create_pidfile()

            pid = tmp_file.read()
            self.assertEqual(pid, b'2')

    @patch('kytos.core.controller.Controller.__init__')
    @patch('kytos.core.controller.Controller.start')
    @patch('kytos.core.controller.Controller.stop')
    def test_restart(self, *args):
        """Test restart method."""
        (mock_stop, mock_start, mock_init) = args
        self.controller.started_at = 1

        graceful = True
        self.controller.restart(graceful)

        mock_stop.assert_called_with(graceful)
        mock_init.assert_called_with(self.controller.options)
        mock_start.assert_called_with(restart=True)

    @patch('kytos.core.controller.Controller.stop_controller')
    def test_stop(self, mock_stop_controller):
        """Test stop method."""
        self.controller.started_at = 1

        graceful = True
        self.controller.stop(graceful)

        mock_stop_controller.assert_called_with(graceful)

    def test_status(self):
        """Test status method."""
        status_1 = self.controller.status()
        self.controller.started_at = 1
        status_2 = self.controller.status()

        self.assertEqual(status_1, 'Stopped')
        self.assertEqual(status_2, 'Running since 1')

    @patch('kytos.core.controller.now')
    def test_uptime(self, mock_now):
        """Test uptime method."""
        mock_now.return_value = 11

        uptime_1 = self.controller.uptime()
        self.controller.started_at = 1
        uptime_2 = self.controller.uptime()

        self.assertEqual(uptime_1, 0)
        self.assertEqual(uptime_2, 10)

    def test_metadata_endpoint(self):
        """Test metadata_endpoint method."""
        req = Request(scope={"type": "http"})
        resp = self.controller.metadata_endpoint(req)
        json_metadata = json.loads(resp.body.decode())

        expected_keys = ['__version__', '__author__', '__license__', '__url__',
                         '__description__']
        self.assertEqual(list(json_metadata.keys()), expected_keys)

    def test_notify_listeners(self):
        """Test notify_listeners method."""
        method = MagicMock()
        self.controller.events_listeners = {'kytos/any': [method]}

        event = MagicMock()
        event.name = 'kytos/any'
        self.controller.notify_listeners(event)

        method.assert_called_with(event)

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

    def test_remove_switch__error(self):
        """Test remove_switch method to error case."""
        switch_1 = MagicMock()
        switch_2 = MagicMock()
        switch_1.dpid = '00:00:00:00:00:00:00:01'
        switch_2.dpid = '00:00:00:00:00:00:00:02'
        self.controller.switches = {switch_1.dpid: switch_1}

        self.controller.remove_switch(switch_2)

        self.assertEqual(self.controller.switches, {switch_1.dpid: switch_1})

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

    @patch('kytos.core.controller.module_from_spec')
    @patch('kytos.core.controller.spec_from_file_location')
    def test_import_napp(self, *args):
        """Test _import_napp method."""
        (mock_spec_from_file, mock_module_from_spec) = args
        napp_spec = MagicMock()
        napp_spec.name = 'spec_name'
        mock_spec_from_file.return_value = napp_spec
        napp_module = MagicMock()
        mock_module_from_spec.return_value = napp_module

        self.controller.options.napps = 'napps'
        self.controller._import_napp('kytos', 'napp')

        self.assertEqual(sys.modules[napp_spec.name], napp_module)
        mock_spec_from_file.assert_called_with('napps.kytos.napp.main',
                                               'napps/kytos/napp/main.py')
        napp_spec.loader.exec_module.assert_called_with(napp_module)

    def test_load_napp__loaded(self):
        """Test load_napp method when napp is already loaded."""
        napp = MagicMock()
        self.controller.napps = {('kytos', 'napp'): napp}

        self.controller.load_napp('kytos', 'napp')

        self.assertEqual(self.controller.napps, {('kytos', 'napp'): napp})

    @patch('kytos.core.controller.Controller._import_napp')
    def test_load_napp__module_not_found(self, mock_import_napp):
        """Test load_napp method when module is not found."""
        mock_import_napp.side_effect = ModuleNotFoundError
        self.controller.napps = {}

        self.controller.load_napp('kytos', 'napp')

        self.assertEqual(self.controller.napps, {})

    @patch('kytos.core.controller.Controller._import_napp')
    def test_load_napp__file_not_found(self, mock_import_napp):
        """Test load_napp method when file is not found."""
        mock_import_napp.side_effect = FileNotFoundError
        self.controller.napps = {}

        self.controller.load_napp('kytos', 'napp')

        self.assertEqual(self.controller.napps, {})

    @patch('kytos.core.api_server.APIServer.register_napp_endpoints')
    @patch('kytos.core.controller.Controller._import_napp')
    def test_load_napp__error(self, *args):
        """Test load_napp method when an error is raised on napp module
           attribution."""
        (mock_import_napp, _) = args
        self.controller.napps = {}

        module = MagicMock()
        module.Main.side_effect = Exception
        mock_import_napp.return_value = module

        with self.assertRaises(KytosNAppSetupException):
            self.controller.load_napp('kytos', 'napp')

        self.assertEqual(self.controller.napps, {})

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

    @patch('kytos.core.controller.Controller.unload_napp')
    def test_unload_napps(self, mock_unload):
        """Test un_load_napps method."""
        napp_tuples = [("kytos", "of_core"), ("kytos", "mef_eline")]
        enabled_napps = []
        expected_calls = []
        for username, napp_name in napp_tuples:
            mock = MagicMock()
            mock.username = username
            mock.name = napp_name
            enabled_napps.append(mock)
            expected_calls.append(call(mock.username, mock.name))
        self.napps_manager.get_enabled_napps.return_value = enabled_napps

        self.controller.unload_napps()
        assert mock_unload.call_count == len(enabled_napps)
        assert mock_unload.mock_calls == list(reversed(expected_calls))

    @patch('kytos.core.controller.import_module')
    def test_reload_napp_module__module_not_found(self, mock_import_module):
        """Test reload_napp_module method when module is not found."""
        mock_import_module.side_effect = ModuleNotFoundError

        with self.assertRaises(ModuleNotFoundError):
            self.controller.reload_napp_module('kytos', 'napp', 'napp_file')

    @patch('kytos.core.controller.reload_module')
    @patch('kytos.core.controller.import_module')
    def test_reload_napp_module__import_error(self, *args):
        """Test reload_napp_module method when an import error occurs."""
        (mock_import_module, mock_reload_module) = args
        napp_module = MagicMock()
        mock_import_module.return_value = napp_module
        mock_reload_module.side_effect = ImportError

        with self.assertRaises(ImportError):
            self.controller.reload_napp_module('kytos', 'napp', 'napp_file')

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

        code = self.controller.reload_napp('kytos', 'napp')

        mock_unload.assert_called_with('kytos', 'napp')
        calls = [call('kytos', 'napp', 'settings'),
                 call('kytos', 'napp', 'main')]
        mock_reload_napp_module.assert_has_calls(calls)
        mock_load.assert_called_with('kytos', 'napp')
        self.assertEqual(code, 200)

    @patch('kytos.core.controller.Controller.unload_napp')
    @patch('kytos.core.controller.Controller.reload_napp_module')
    def test_reload_napp__error(self, *args):
        """Test reload_napp method to error case."""
        (mock_reload_napp_module, _) = args
        mock_reload_napp_module.side_effect = ModuleNotFoundError

        code = self.controller.reload_napp('kytos', 'napp')

        self.assertEqual(code, 400)

    @patch('kytos.core.controller.Controller.reload_napp', return_value=200)
    def test_rest_reload_napp(self, mock_reload_napp):
        """Test rest_reload_napp method."""
        req = Request(
            scope={
                "type": "http",
                "path_params": {"username": "kytos", "napp_name": "napp"},
            }
        )
        resp = self.controller.rest_reload_napp(req)

        mock_reload_napp.assert_called_with('kytos', 'napp')
        self.assertEqual(json.loads(resp.body.decode()), 'reloaded')
        self.assertEqual(resp.status_code, 200)

    @patch('kytos.core.controller.Controller.reload_napp')
    def test_rest_reload_all_napps(self, mock_reload_napp):
        """Test rest_reload_all_napps method."""
        req = Request(
            scope={
                "type": "http",
                "path_params": {"username": "kytos", "napp_name": "napp"},
            }
        )
        self.controller.napps = [('kytos', 'napp')]
        resp = self.controller.rest_reload_all_napps(req)

        mock_reload_napp.assert_called_with('kytos', 'napp')
        self.assertEqual(json.loads(resp.body.decode()), 'reloaded')
        self.assertEqual(resp.status_code, 200)

    def test_init_attrs(self):
        """Test init attrs."""
        self.controller.start_auth()
        assert self.controller.auth
        assert self.controller.dead_letter


class TestControllerAsync:

    """TestControllerAsync."""

    async def test_start_controller(self, controller, monkeypatch):
        """Test start controller."""
        controller._buffers = KytosBuffers()
        controller.loop = MagicMock()
        server = MagicMock()
        monkeypatch.setattr("kytos.core.controller.KytosServer", server)
        napp = MagicMock()
        controller._pool = MagicMock()
        controller.pre_install_napps = MagicMock()
        controller.api_server = MagicMock()
        controller.load_napps = MagicMock()
        controller.options.napps_pre_installed = [napp]
        controller.start_controller()
        assert controller.buffers

        controller.server.serve_forever.assert_called()
        all_buffers = controller.buffers.get_all_buffers()
        # It's expected that all buffers have a task + the api server task
        assert controller.loop.create_task.call_count == len(all_buffers) + 1
        assert len(controller._tasks) == len(all_buffers) + 1
        controller.pre_install_napps.assert_called_with([napp])
        controller.load_napps.assert_called()
        controller.api_server.start_web_ui.assert_called()

    async def test_stop_controller(self, controller):
        """Test stop_controller method."""
        controller.loop = MagicMock()
        api_server = MagicMock()
        napp_dir_listener = MagicMock()
        controller.server = MagicMock()
        controller.unload_napps = MagicMock()
        controller._buffers = MagicMock()
        controller.api_server = api_server
        controller.napp_dir_listener = napp_dir_listener

        controller.stop_controller()

        controller.buffers.send_stop_signal.assert_called()
        api_server.stop.assert_called()
        napp_dir_listener.stop.assert_called()
        controller.unload_napps.assert_called()
        controller.server.shutdown.assert_called()
        controller.loop.stop.assert_called()

    async def test_raw_event_handler(self, controller):
        """Test raw_event_handler async method by handling a shutdown event."""
        controller._buffers = KytosBuffers()
        event = KytosEvent("kytos/core.shutdown")
        controller.notify_listeners = MagicMock()
        await controller.buffers.raw._queue.async_q.put(event)
        await controller.event_handler("raw")
        controller.notify_listeners.assert_called_with(event)

    async def test_msg_in_event_handler(self, controller):
        """Test msg_in_event_handler async method by handling a shutdown
           event."""
        controller._buffers = KytosBuffers()
        event = KytosEvent("kytos/core.shutdown")
        controller.notify_listeners = MagicMock()
        await controller.buffers.msg_in._queue.async_q.put(event)
        await controller.event_handler("msg_in")
        controller.notify_listeners.assert_called_with(event)

    async def test_msg_out_event_handler(self, controller):
        """Test msg_out_event_handler async method by handling a common and a
           shutdown event."""
        controller._buffers = KytosBuffers()
        controller.notify_listeners = MagicMock()
        dst = MagicMock()
        dst.state = 0
        packet = MagicMock()
        msg = MagicMock()
        msg.pack.return_value = packet

        event_1 = KytosEvent('kytos/core.any',
                             content={'message': msg, 'destination': dst})
        event_2 = KytosEvent('kytos/core.shutdown')

        await controller.buffers.msg_out._queue.async_q.put(event_1)
        await controller.buffers.msg_out._queue.async_q.put(event_2)
        await controller.msg_out_event_handler()
        dst.send.assert_called_with(packet)
        controller.notify_listeners.assert_called_with(event_1)

    async def test_msg_out_event_handler_pack_exc(self, controller):
        """Test msg_out_event_handler async pack exception."""
        controller._buffers = KytosBuffers()
        dst, msg = MagicMock(), MagicMock()
        dst.state = 0
        msg.pack.side_effect = PackException("some error")
        event_1 = KytosEvent('kytos/core.any',
                             content={'message': msg, 'destination': dst})
        event_2 = KytosEvent('kytos/core.shutdown')

        await controller.buffers.msg_out._queue.async_q.put(event_1)
        await controller.buffers.msg_out._queue.async_q.put(event_2)
        await controller.msg_out_event_handler()
        assert controller.log.error.call_count == 1

    async def test_app_event_handler(self, controller):
        """Test app_event_handler async method by handling a shutdown event."""
        controller._buffers = KytosBuffers()
        event = KytosEvent("kytos/core.shutdown")
        controller.notify_listeners = MagicMock()
        await controller.buffers.app._queue.async_q.put(event)
        await controller.event_handler("app")
        controller.notify_listeners.assert_called_with(event)

    async def test_configuration_endpoint(self, controller, api_client):
        """Should return the attribute options as json."""
        expected = vars(controller.options)
        expected.pop("jwt_secret", None)
        resp = await api_client.get("kytos/core/config")
        assert resp.status_code == 200
        assert expected == resp.json()
