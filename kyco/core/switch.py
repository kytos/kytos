# -*- coding: utf-8 *-*
"""Module with main classes related to Switches"""
import logging
from socket import error as SocketError
from socket import socket as Socket

from kyco.constants import CONNECTION_TIMEOUT
from kyco.core.exceptions import KycoSwitchOfflineException
from kyco.utils import now

__all__ = ('KycoSwitch',)

log = logging.getLogger('Kyco')

class Connection(object):
        def __init__(self, address, port, socket, dpid=None):
            self.address = address
            self.port = port
            self.socket = socket
            self.dpid = dpid

        @property
        def id(self):
            if self.dpid is not None:
                return self.dpid
            else:
                return (self.address, self.port)

        def send(self, buffer):
            try:
                self.socket.send(buffer)
            except (OSError, SocketError) as exception:
                self.close()
                raise exception

        def close(self):
            if self.socket:
                self.socket.close()
                self.socket = None # TODO: I dont know if this is necessary

        def is_connected(self):
            return self.socket is not None


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
    def __init__(self, dpid, connection=None, ofp_version='0x01', features=None):
        self.dpid = dpid
        self.connection = connection
        self.ofp_version = ofp_version
        self.features = features
        self.firstseen = now()
        self.lastseen = now()
        self.sent_xid = None
        self.waiting_for_reply = False
        self.request_timestamp = 0
        #: Dict associating mac addresses to switch ports.
        #:      the key of this dict is a mac_address, and the value is a set
        #:      containing the ports of this switch in which that mac can be
        #:      found.
        self.mac2port = {}
        #: This flood_table will keep track of flood packets to avoid over
        #:     flooding on the network. Its key is a hash composed by
        #:     (eth_type, mac_src, mac_dst) and the value is the timestamp of
        #:      the last flood.
        self.flood_table = {}

    def disconnect(self):
        """Disconnect the switch.

        """
        self.connection.close()
        self.connection = None
        log.info("Switch %s is disconnected", self.dpid)

    def is_active(self):
        return (now() - self.lastseen).seconds <= CONNECTION_TIMEOUT

    def is_connected(self):
        """Verifies if the switch is connected to a socket.
        """
        return self.connection.is_connected() and self.is_active()

#    def save_connection(self, socket, connection_id):
#        """Save a new connection to the existing switch.
#
#        Args:
#            socket (socket): Socket connection to the switch
#            connection_id (tuple): Tuple with ip and port from the switch
#        Raises:
#            # TODO: raise proper exceptions
#            ...: The passed attribute is not a socket connection
#            ...: This switch is already connected to a socket
#        """
#        if not isinstance(socket, Socket):
#            raise Exception("The passed argument is not a python socket")
#
#        if self.is_connected():
#            error_message = "Kyco already have a switch ({}) connected at {} "
#            raise Exception(error_message.format(self.dpid,
#                                                 self.connection_id))
#
#        self.socket = socket
#        self.connection_id = connection_id

    def send(self, buffer):
        """Sends data to the switch.

        Args:
            buffer (bytes): bytes to be sent to the switch throught its
                            connection.
        Raises:
            # TODO: raise proper exceptions on the code
            ......: If the switch connection was connection.
            ......: If the passed `data` is not a bytes object
        """
        if self.connection:
            self.connection.send(buffer)

    def update_lastseen(self):
        self.lastseen = now()
