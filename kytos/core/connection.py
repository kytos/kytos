"""Module with main classes related to Connections."""
import logging
from enum import Enum
from errno import EBADF, ENOTCONN
from socket import error as SocketError
from socket import SHUT_RDWR

__all__ = ('Connection', 'ConnectionProtocol', 'CONNECTION_STATE')

log = logging.getLogger(__name__)


class CONNECTION_STATE(Enum):
    """Enum of possible general connections states."""

    NEW = 0
    SETUP = 1
    ESTABLISHED = 2
    FAILED = 3
    FINISHED = 4


class ConnectionProtocol:
    """Class to hold simple protocol information for the connection."""

    def __init__(self, name=None, version=None, state=None):
        """Constructor for the connection protocol class."""
        self.name = name
        self.version = version
        self.state = state


class Connection(object):
    """Connection class to abstract a network connections."""

    def __init__(self, address, port, socket, switch=None):
        """The constructor method have the below parameters.

        Parameters:
          address (HWAddress): Source address.
          port (int): Port number.
          socket (socket): socket.
          switch (:class:`~.core.switch.Switch`): switch with this connection.
        """
        self.address = address
        self.port = port
        self.socket = socket
        self.switch = switch
        self.state = CONNECTION_STATE.NEW
        self.protocol = ConnectionProtocol()
        self.remaining_data = b''

    @property
    def state(self):
        """Return the state of the connection."""
        return self._state

    @state.setter
    def state(self, new_state):
        if new_state not in CONNECTION_STATE:
            raise Exception('Unknown State', new_state)
        self._state = new_state # noqa
        log.debug('Connection %s changed state: %s',
                  self.id, self.state)

    @property
    def id(self):
        """Return id from Connection instance.

        Returns:
            id (string): Connection id.
        """
        return (self.address, self.port)

    def send(self, buffer):
        """Send a buffer message using the socket from the connection instance.

        Parameters:
            buffer (bytes): Message buffer that will be sent.
        """
        try:
            if self.is_alive():
                self.socket.sendall(buffer)
        except (OSError, SocketError) as exception:
            log.debug('Could not send packet. Exception: %s', exception)
            self.close()

    def close(self):
        """Close the socket from connection instance."""
        self.state = CONNECTION_STATE.FINISHED
        if self.socket:
            log.debug('Shutting down Connection %s', self.id)
            try:
                self.socket.shutdown(SHUT_RDWR)
                self.socket.close()
            except OSError as e:
                if e.errno not in (ENOTCONN, EBADF):
                    raise e
            self.socket = None
            log.debug('Connection Closed: %s', self.id)

        if self.switch and self.switch.connection is self:
            self.switch.connection = None

    def is_alive(self):
        """Return True if the connection socket is alive. False otherwise."""
        return self.socket is not None and self.state not in (
            CONNECTION_STATE.FINISHED, CONNECTION_STATE.FAILED)

    def is_new(self):
        """Return True if the connection is new. False otherwise."""
        return self.state == CONNECTION_STATE.NEW

    def is_established(self):
        """Return True if the connection is established. False otherwise."""
        return self.state == CONNECTION_STATE.ESTABLISHED

    def is_during_setup(self):
        """Return True if the connection is in setup state. False otherwise."""
        return self.state == CONNECTION_STATE.SETUP

    def set_established_state(self):
        """Set the connection state to Established."""
        self.state = CONNECTION_STATE.ESTABLISHED

    def set_setup_state(self):
        """Set the connection state to Setup."""
        self.state = CONNECTION_STATE.SETUP

    def update_switch(self, switch):
        """Update switch with this instance of Connection.

        Parameters:
          switch (:class:`~.core.switch.Switch`): switch instance.
        """
        self.switch = switch
        self.switch.connection = self
