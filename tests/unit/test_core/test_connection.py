"""Test kytos.core.connection module."""
from socket import error as SocketError
from unittest.mock import MagicMock

import pytest

from kytos.core.connection import Connection, ConnectionState


class TestConnection:
    """Connection tests."""

    def setup_method(self):
        """Instantiate a Connection."""
        socket = MagicMock()
        switch = MagicMock()
        self.connection = Connection('addr', 123, socket, switch)

        switch.connection = self.connection

    def test__str__(self):
        """Test __str__ method."""
        assert str(self.connection) == "Connection('addr', 123)"

    def test__repr__(self):
        """Test __repr__ method."""
        self.connection.socket = 'socket'
        self.connection.switch = 'switch'

        expected = "Connection('addr', 123, 'socket', 'switch', " + \
                   "<ConnectionState.NEW: 0>)"
        assert repr(self.connection) == expected

    def test_state(self):
        """Test state property."""
        assert self.connection.state.value == 0

        self.connection.state = ConnectionState.FINISHED
        assert self.connection.state.value == 4

    def test_state__error(self):
        """Test state property to error case."""
        with pytest.raises(Exception):
            self.connection.state = 1000

    def test_id(self):
        """Test id property."""
        assert self.connection.id == ('addr', 123)

    def test_send(self):
        """Test send method."""
        self.connection.send(b'data')

        self.connection.socket.sendall.assert_called_with(b'data')

    def test_send_error(self):
        """Test send method to error case."""
        self.connection.socket.sendall.side_effect = SocketError

        with pytest.raises(SocketError):
            self.connection.send(b'data')

        assert self.connection.socket is None

    def test_close(self):
        """Test close method."""
        self.connection.close()

        assert self.connection.socket is None
        assert self.connection is not None

    def test_close__os_error(self):
        """Test close method to OSError case."""
        self.connection.socket.shutdown.side_effect = OSError

        with pytest.raises(OSError):
            self.connection.close()

        assert self.connection.socket is not None

    def test_close__attribute_error(self):
        """Test close method to AttributeError case."""
        self.connection.socket = None

        self.connection.close()

        assert self.connection.socket is None

    def test_is_alive(self):
        """Test is_alive method to True and False returns."""
        assert self.connection.is_alive()

        self.connection.state = ConnectionState.FINISHED
        assert not self.connection.is_alive()

    def test_is_new(self):
        """Test is_new method."""
        assert self.connection.is_new()

    def test_established_state(self):
        """Test set_established_state and is_established methods."""
        self.connection.set_established_state()
        assert self.connection.is_established()

    def test_setup_state(self):
        """Test set_setup_state and is_during_setup methods."""
        self.connection.set_setup_state()
        assert self.connection.is_during_setup()

    def test_update_switch(self):
        """Test update_switch method."""
        switch = MagicMock()
        self.connection.update_switch(switch)

        assert self.connection.switch == switch
        assert switch.connection == self.connection
