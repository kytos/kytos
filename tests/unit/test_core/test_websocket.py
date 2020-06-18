"""Test kytos.core.websocket module."""
import logging
from copy import copy
from unittest import TestCase
from unittest.mock import Mock

from kytos.core.logs import LogManager


class TestWebSocketLog(TestCase):
    """Test special requirements for web socket logging."""

    def test_no_requests_logging(self):
        """Should not log web requests to avoid an infinite logging loop.

        Do not log any level below warning.
        """
        # Save original state
        handlers_bak = copy(logging.root.handlers)

        logging.root.handlers = []
        socket = Mock()
        LogManager.enable_websocket(socket)
        # Lower logger level simulating logging.ini config
        web_logger = logging.getLogger('werkzeug')
        web_logger.setLevel(logging.DEBUG)

        web_logger.info('should not log')
        self.assertEqual(0, socket.call_count)
        web_logger.warning('should log')
        self.assertEqual(1, socket.emit.call_count)

        # Restore original state
        logging.root.handlers = handlers_bak
