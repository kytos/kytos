"""Test the LogManager class."""
import logging
from inspect import FrameInfo
from unittest import TestCase
from unittest.mock import Mock, call, patch

from kytos.core.logs import LogManager, NAppLog


class TestLogs(TestCase):
    """Test the log manager class."""

    def setUp(self):
        """Prepare root logger mocked stream handler."""
        root_log = logging.getLogger()
        # Remove all handlers
        self._handlers_backup = root_log.handlers
        root_log.handlers = []
        # Add a handler with mocked stream
        self._stream = Mock()
        self._handler = LogManager.add_stream_handler(self._stream)

    def tearDown(self):
        """Restore root logger handlers."""
        logging.getLogger().handlers = self._handlers_backup

    def test_parent_handler_usage(self):
        """A logger should use parent's handler."""
        self._set_format('%(message)s')
        log = logging.getLogger('log')
        message = 'test message'
        log.critical(message)
        # Although parent's handler is not in "log", it will be used
        self.assertNotIn(self._handler, log.handlers)
        self._assert_stream_write(message)

    @patch('kytos.core.logs.inspect')
    def test_napp_id_detection(self, inspect_mock):
        """Test NApp ID detection based on filename."""
        # Mocked stack with a NApp filename
        filename = '/napps/username/name/main.py'
        frame = FrameInfo(None, filename, None, None, None, None)
        inspect_mock.stack.return_value = [frame]

        self._set_format('%(name)s')
        log = NAppLog()
        log.critical('Hello, world!')
        self._assert_stream_write('username/name')

    def _set_format(self, fmt):
        formatter = logging.Formatter(fmt)
        self._handler.setFormatter(formatter)

    def _assert_stream_write(self, text):
        self.assertIn(call(text), self._stream.write.call_args_list)
