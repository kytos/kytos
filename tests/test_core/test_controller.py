"""Test kytos.core.controller module."""
import logging
from copy import copy
from unittest import TestCase
from unittest.mock import Mock, patch

from kytos.core import Controller


class TestController(TestCase):
    """Test the Controller class."""

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
