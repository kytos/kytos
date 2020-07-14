"""Test kytos.core.helpers module."""
from unittest import TestCase
from unittest.mock import patch

from kytos.core.helpers import get_time, run_on_thread


class TestHelpers(TestCase):
    """Test the helpers methods."""

    @staticmethod
    @patch('kytos.core.helpers.Thread')
    def test_run_on_thread(mock_thread):
        """Test run_on_thread decorator."""

        @run_on_thread
        def test():
            pass

        test()

        mock_thread.return_value.start.assert_called()

    def test_get_time__str(self):
        """Test get_time method passing a string as parameter."""
        date = get_time("2000-01-01T00:30:00")

        self.assertEqual(date.year, 2000)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)
        self.assertEqual(date.hour, 0)
        self.assertEqual(date.minute, 30)
        self.assertEqual(date.second, 0)

    def test_get_time__dict(self):
        """Test get_time method passing a dict as parameter."""
        date = get_time({"year": 2000,
                         "month": 1,
                         "day": 1,
                         "hour": 00,
                         "minute": 30,
                         "second": 00})

        self.assertEqual(date.year, 2000)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)
        self.assertEqual(date.hour, 0)
        self.assertEqual(date.minute, 30)
        self.assertEqual(date.second, 0)

    def test_get_time__none(self):
        """Test get_time method by not passing a parameter."""
        date = get_time()

        self.assertIsNone(date)
