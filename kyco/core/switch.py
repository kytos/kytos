# -*- coding: utf-8 *-*
"""Module with main classes related to Switches"""
import logging
from socket import socket as Socket, error as SocketError

from kyco.constants import POOLING_TIME
from kyco.utils import now

__all__ = ('KycoSwitch',)

log = logging.getLogger('Kyco')


class KycoSwitch(object):
    """This is the main class related to Switches modeled on Kyco.

    A new KycoSwitch will be created every time the handshake process is done
    (after receiving the first FeaturesReply). Considering this, the
    :attr:`socket`, :attr:`connection_id`, :attr:`of_version` and
    :attr:`features` need to be passed on init. But when the connection to the
    switch is lost, then this attributes can be set to None (actually some of
    them must be).

    The :attr:`dpid` attribute will be the unique identifier of a KycoSwitch.
    It is the :attr:`pyof.*.controller2switch.SwitchFeatures.datapath-id` that
    defined by the OpenFlow Specification, it is a 64 bit field that should be
    thought of as analogous to a Ethernet Switches bridge MAC, its a unique
    identifier for the specific packet processing pipeline being managed. One
    physical switch may have more than one datapath-id (think virtualization of
    the switch).

    :attr:`socket` is the request from a TCP connection, it represents the
    effective connection between the switch and the controller.

    :attr:`connection_id` is a tuple, composed by the ip and port of the
    stabilished connection (if any). It will be used to help map the connection
    to the KycoSwitch and vice-versa.

    :attr:`ofp_version` is a string representing the accorded version of
    python-openflow that will be used on the communication between the
    Controller and the KycoSwitch.

    :attr:`features` is an instance of
    :class:`pyof.*.controller2switch.FeaturesReply` representing the current
    featues of the switch.

    Args:
        dpid (): datapath_id of the switch
        socket (socket): Socket/Request
        connection_id (tuple): Tuple `(ip, port)`
        ofp_version (string): Current talked OpenFlow version
        features (FeaturesReply): FeaturesReply (from python-openflow) instance
    """
    def __init__(self, dpid, socket, connection_id, ofp_version='0x01',
                 features=None):
        self.dpid = dpid
        self.socket = socket
        self.connection_id = connection_id  # (ip, port)
        self.ofp_version = ofp_version
        self.features = features
        self.firstseen = now()
        self.lastseen = now()
        self.sent_xid = None
        self.waiting_for_reply = False
        self.request_timestamp = 0

    def disconnect(self):
        """Disconnect the switch.

        Closes the current socket and set None on the :attr:`socket` and
        attr:`connection_id` attributes
        """
        try:
            if self.socket is not None:
                self.socket.close()
                msg = 'Socket {} from switch {} closed'
                msg = msg.format(self.connection_id, self.dpid)
                log.info(msg)
        except SocketError:
            pass

        self.socket = None
        self.connection_id = None

    def is_connected(self):
        """Verifies if the switch is connected to a socket.

        Try sending a null byte to the switch to check if the connection is
        still alive.

        Returns:
            True: if the connection is alive
            False: if not.
        """
        if (now() - self.lastseen).seconds > POOLING_TIME*2:
            self.disconnect()
            return False
        else:
            return True

    def save_connection(self, socket, connection_id):
        """Save a new connection to the existing switch.

        Args:
            socket (socket): Socket connection to the switch
            connection_id (tuple): Tuple with ip and port from the switch
        Raises:
            # TODO: raise proper exceptions
            ...: The passed attribute is not a socket connection
            ...: This switch is already connected to a socket
        """
        if not isinstance(socket, Socket):
            raise Exception("The passed argument is not a python socket")

        if self.is_connected():
            error_message = "Kyco already have a switch ({}) connected at {} "
            raise Exception(error_message.format(self.dpid,
                                                 self.connection_id))

        self.socket = socket
        self.connection_id = connection_id

    def send(self, data):
        """Sends data to the switch.

        Args:
            data (bytes): bytes data to be sent to the switch throught its
                socket connection.
        Raises:
            # TODO: raise proper exceptions on the code
            ......: If the switch connection was connection.
            ......: If the passed `data` is not a bytes object
        """
        if not isinstance(data, bytes):
            raise Exception("You can only send bytes data to the switch")

        if not self.socket:
            raise Exception("This switch is not connected")

        try:
            self.socket.send(data)
        except SocketError:
            self.disconnect()

    def update_lastseen(self):
        self.lastseen = now()
