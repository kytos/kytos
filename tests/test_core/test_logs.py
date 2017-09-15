"""Test the logs module."""
import imp
import logging
from copy import copy
from inspect import FrameInfo
from unittest import TestCase
from unittest.mock import Mock, patch

from kytos.core import logs
from kytos.core.logs import LogManager, NAppLog


class LogTester(TestCase):
    """Common code to test loggers."""

    def setUp(self):
        """Backup original handlers."""
        self._patcher = None
        self._logger = None
        # If we don't copy, it'll be a reference to a list that will be changed
        self._handlers_bak = copy(logging.getLogger().handlers)

    def tearDown(self):
        """Undo mocking, restore handlers."""
        if self._patcher:
            self._patcher.stop()
        logging.getLogger().handlers = self._handlers_bak

    def _mock_logger(self):
        """Mock kytos.core.log and assign to self._logger.

        Calling this function is required for ``_has_string_in_log``.
        """
        self._patcher = patch('kytos.core.logs.LOG')
        self._logger = self._patcher.start()

    def _assert_string_in_logs(self, string):
        """Assert _string_ is in any message sent to the root logger.

        Search through all log messages since ``_mock_logger`` was called.
        """
        msgs = [call[1][0] for call in self._logger.mock_calls]
        self.assertTrue(any(string in msg for msg in msgs),
                        f'Message "{string}" not in {msgs}.')


class TestLogManager(LogTester):
    """Test LogManager class."""

    def test_add_handler_to_root(self):
        """Handler should be added to root logger."""
        handler = Mock()
        LogManager.add_handler(handler)
        self.assertIn(handler, logging.root.handlers)

    @staticmethod
    @patch('kytos.core.logs.LogManager._PARSER')
    @patch('kytos.core.logs.Path')
    def test_custom_formatter(path, parser):
        """Should use a custom formatter instead of Python's default."""
        path.return_value.exists.return_value = False
        # Make sure we have the custome formatter section
        parser.__contains__.return_value = True
        handler = Mock()

        LogManager.add_handler(handler)
        handler.setFormatter.assert_called_once()

    def test_add_websocket(self):
        """A stream should be used in a handler added to the root logger."""
        socket = Mock()
        handler = LogManager.enable_websocket(socket)
        self.assertIn(handler, logging.root.handlers)

    @staticmethod
    def test_parent_handler_usage():
        """Existent logger should use a new handler."""
        # First, get a child logger.
        old_logger = logging.getLogger('non-root logger')
        # Then, add a new handler.
        new_handler = Mock(level=logging.DEBUG)
        LogManager.add_handler(new_handler)

        old_logger.setLevel(logging.DEBUG)
        old_logger.debug('Handler should receive me.')
        new_handler.handle.assert_called_once()

    @patch('kytos.core.logs.Path')
    def test_non_existent_config_file(self, path):
        """If config file doesn't exist, warn instead of raising exception."""
        self._mock_logger()
        path.return_value.exists.return_value = False
        LogManager.load_config_file('non_existent_file')
        self._assert_string_in_logs('Log config file "%s" does not exist.')

    @patch.object(LogManager, '_PARSER')
    @patch('kytos.core.logs.config')
    @patch('kytos.core.logs.Path')
    def test_no_syslog(self, path, config, parser):
        """Must log when there's no syslog and try again without it."""
        path.return_value.exists.return_value = True
        config.fileConfig.side_effect = [OSError, None]
        parser.__contains__.return_value = True  # must have syslog section
        self._mock_logger()

        LogManager.load_config_file('existent_file')
        self._assert_string_in_logs('Trying to disable syslog')
        parser.remove_section.assert_called_once_with('handler_syslog')
        self._assert_string_in_logs('Logging config file "%s" loaded '
                                    'successfully.')

    @patch('kytos.core.logs.Path')
    @patch('kytos.core.logs.config')
    def test_config_file_exception(self, config, path):
        """Test other errors (e.g. /dev/log permission)."""
        path.return_value.exists.return_value = True
        config.fileConfig.side_effect = OSError

        self._mock_logger()
        LogManager.load_config_file('existent_file')
        self._assert_string_in_logs('Using default Python logging config')

    @patch.object(LogManager, '_PARSER')
    @patch('kytos.core.logs.Path')
    @patch('kytos.core.logs.config')
    def test_set_debug_mode(self, config, path, parser):
        """Test set_debug_mode with debug = True."""
        path.return_value.exists.return_value = True
        config.fileConfig.side_effect = OSError

        self._mock_logger()
        LogManager.load_config_file('existent_file', debug=True)

        expected_message = 'Setting log configuration with debug mode.'
        self._assert_string_in_logs(expected_message)

        parser.set('logger_root', 'level', 'DEBUG')
        parser.set.assert_called_with('logger_root', 'level', 'DEBUG')

        parser.set('logger_api_server', 'level', 'DEBUG')
        parser.set.assert_called_with('logger_api_server', 'level', 'DEBUG')

    @patch('kytos.core.logs.LogManager._PARSER')
    @patch('kytos.core.logs.Path')
    @patch('kytos.core.logs.config')
    def test_set_debug_mode_with_false(self, config, path, parser):
        """Test set_debug_mode with debug = False."""
        path.return_value.exists.return_value = True
        config.fileConfig.side_effect = OSError

        self._mock_logger()
        LogManager.load_config_file('existent_file', debug=False)

        parser.set.assert_not_called()

    def test_handler_filter(self):
        """Should not log harmless werkzeug "session is disconnected" msg."""
        logging.root.handlers = []

        handler = Mock(level=logging.WARNING)
        LogManager.add_handler(handler)

        # Message based on the log output that ends with traceback plaintext as
        # seen in lib/python3.6/site-packages/werkzeug/serving.py:225 of
        # Werkzeug==0.12.1
        msg = "lorem ipsum KeyError: 'Session is disconnected'"
        logger = logging.getLogger('werkzeug')
        logger.setLevel(logging.ERROR)
        with patch.object(handler, 'emit'):
            logger.error('lorem ipsum %s', msg)
            self.assertEqual(0, handler.emit.call_count)

    @staticmethod
    def test_old_handler_filter():
        """Should not log harmless werkzeug "session is disconnected" msg.

        The filter should be added to all root handlers, even the ones that
        already existed before importing the "logs" module.

        Message based on the log output that ends with traceback plaintext as
        seen in lib/python3.6/site-packages/werkzeug/serving.py:225 of
        Werkzeug==0.12.1:

            - logger name: werkzeug
            - level: ERROR
            - only argument: ends with "KeyError: 'Session is disconnected'"
        """
        old_handler = Mock()
        old_handler.filters = []

        logging.root.addHandler(old_handler)
        old_handler.addFilter.assert_not_called()
        # Importing the module should add the filter to existent root handlers.
        imp.reload(logs)
        old_handler.addFilter.assert_called_once_with(
            logs.LogManager.filter_session_disconnected)

        logging.root.removeHandler(old_handler)


class TestNAppLog(LogTester):
    """Test the log used by NApps."""

    def setUp(self):
        """Initialize variables."""
        super().setUp()
        self._inspect_patcher = None

    def tearDown(self):
        """Undo mocking."""
        super().tearDown()
        if self._inspect_patcher:
            self._inspect_patcher.stop()

    def _set_filename(self, filename):
        """Mock the NApp's main.py file path."""
        # Put the filename in the call stack
        frame = FrameInfo(None, filename, None, None, None, None)
        self._inspect_patcher = patch('kytos.core.logs.inspect')
        inspect = self._inspect_patcher.start()
        inspect.stack.return_value = [frame]

    def test_napp_id_detection(self):
        """Test NApp ID detection based on filename."""
        self._set_filename('/napps/username/name/main.py')
        expected_logger_name = 'username/name'
        napp_logger = NAppLog()
        self.assertEqual(expected_logger_name, napp_logger.name)

    def test_napp_id_not_found(self):
        """If NApp ID is not found, should use root logger."""
        self._set_filename('not/an/expected/NApp/path.py')
        root_logger = logging.getLogger()
        napp_logger = NAppLog()
        self.assertEqual(root_logger.name, napp_logger.name)
