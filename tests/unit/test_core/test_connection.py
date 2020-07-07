"""Test kytos.core.connection module."""
from unittest import TestCase
from unittest.mock import MagicMock

from kytos.core.connection import Connection, ConnectionState


class TestConnection(TestCase):
    """Connection tests."""

    def setUp(self):
        """Instantiate a Connection."""
        socket = MagicMock()
        self.connection = Connection('addr', 123, socket)
        self.connection.socket = MagicMock()

    def test__str__(self):
        """Test __str__ method."""
        self.assertEqual(str(self.connection), "Connection('addr', 123)")

    def test__repr__(self):
        """Test __repr__ method."""
        self.connection.socket = 'socket'
        self.connection.switch = 'switch'

        expected = "Connection('addr', 123, 'socket', 'switch', " + \
                   "<ConnectionState.NEW: 0>)"
        self.assertEqual(repr(self.connection), expected)

    def test_state(self):
        """Test state property."""
        self.assertEqual(self.connection.state.value, 0)

        self.connection.state = ConnectionState.FINISHED
        self.assertEqual(self.connection.state.value, 4)

    def test_id(self):
        """Test id property."""
        self.assertEqual(self.connection.id, ('addr', 123))

    def test_send(self):
        """Test send method."""
        self.connection.send(b'data')

        self.connection.socket.sendall.assert_called_with(b'data')

    def test_close(self):
        """Test close method."""
        self.connection.close()

        self.assertIsNone(self.connection.socket)

    def test_is_alive(self):
        """Test is_alive method to True and False returns."""
        self.assertTrue(self.connection.is_alive())

        self.connection.state = ConnectionState.FINISHED
        self.assertFalse(self.connection.is_alive())

    def test_is_new(self):
        """Test is_new method."""
        self.assertTrue(self.connection.is_new())

    def test_established_state(self):
        """Test set_established_state and is_established methods."""
        self.connection.set_established_state()
        self.assertTrue(self.connection.is_established())

    def test_setup_state(self):
        """Test set_setup_state and is_during_setup methods."""
        self.connection.set_setup_state()
        self.assertTrue(self.connection.is_during_setup())

    def test_update_switch(self):
        """Test update_switch method."""
        switch = MagicMock()
        self.connection.update_switch(switch)

        self.assertEqual(self.connection.switch, switch)
        self.assertEqual(switch.connection, self.connection)
