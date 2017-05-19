"""Test Kytos logs."""
from unittest import TestCase
from unittest.mock import Mock, patch

from kytos.core.logs import LogManager


class TestLogs(TestCase):
    """Test Kytos logs."""

    @staticmethod
    @patch('kytos.core.logs.Path')
    @patch('kytos.core.logs.getLogger')
    def test_non_existent_config_file(getLogger, Path):
        """If config file doesn't exist, warn instead of raising exception."""
        log = Mock()
        getLogger.return_value = log
        Path.return_value.exists.return_value = False
        LogManager.load_logging_file('I will never exist!')
        log.warning.assert_called()
