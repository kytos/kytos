"""Module with main classes related to Switches"""
import logging
import json

from socket import error as SocketError

from kyco.constants import CONNECTION_TIMEOUT, FLOOD_TIMEOUT
from kyco.utils import now

__all__ = ('Switch',)

log = logging.getLogger('Kyco')


class Interface(object):
    def __init__(self, name, port_number, switch, address=None, state=None):
        self.name = name
        self.port_number = int(port_number)
        self.switch = switch
        self.address = address
        self.state = state
        self.endpoints = []

    def __eq__(self, other):
        if isinstance(other,str):
            return self.address == other

        if not isinstance(other,Interface):
            return False

        if self.port_number != other.port_number:
            return False

        if self.name != other.name:
            return False

        if self.address != other.address:
            return False

        if self.switch.dpid != self.switch.dpid:
            return False

        return True

    @property
    def id(self):
        return "{}:{}".format(self.switch.dpid, self.port_number)

    def get_endpoint(self, endpoint):
        for item in self.endpoints:
            if endpoint == item[0]:
                return item
        return None

    def is_link_between_switches(self):
        for endpoint, timestamp in self.endpoints:
            if type(endpoint) is Interface:
                return True
        return False

    def add_endpoint(self, endpoint):
        exists = self.get_endpoint(endpoint)
        if not exists:
            self.endpoints.append((endpoint, now()))

    def delete_endpoint(self, endpoint):
        exists = self.get_endpoint(endpoint)
        if exists:
            self.endpoints.remove(exists)

    def update_endpoint(self, endpoint):
        exists = self.get_endpoint(endpoint)
        if exists:
            self.delete_endpoint(endpoint)
        self.add_endpoint(endpoint)

    def as_dict(self):
        return {'id': self.id,
                'name': self.name,
                'port_number': self.port_number,
                'switch': self.switch.dpid,
                'class': 'interface'}

    def as_json(self):
        return json.dumps(self.as_dict())


class Connection(object):
    def __init__(self, address, port, socket, switch=None):
        self.address = address
        self.port = port
        self.socket = socket
        self.switch = switch

    @property
    def id(self):
        return (self.address, self.port)

    def send(self, buffer):
        try:
            self.socket.send(buffer)
        except (OSError, SocketError) as exception:
            self.close()
            # TODO: Raise or create an error event?
            raise exception

    def close(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None  # TODO: Is this really necessary?

        if self.switch.connection is self:
            self.switch.connection = None

    def is_connected(self):
        return self.socket is not None

    def update_switch(self, switch):
        self.switch = switch
        self.switch.connection = self


class Switch(object):
    """This is the main class related to Switches modeled on Kyco.

    A new Switch will be created every time the handshake process is done
    (after receiving the first FeaturesReply). Considering this, the
    :attr:`socket`, :attr:`connection_id`, :attr:`of_version` and
    :attr:`features` need to be passed on init. But when the connection to the
    switch is lost, then this attributes can be set to None (actually some of
    them must be).

    The :attr:`dpid` attribute will be the unique identifier of a Switch.
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
    to the Switch and vice-versa.

    :attr:`ofp_version` is a string representing the accorded version of
    python-openflow that will be used on the communication between the
    Controller and the Switch.

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
    def __init__(self, dpid, connection=None, ofp_version='0x01',
                 features=None):
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
        self.interfaces = {}
        self.flows = []

        if connection:
            connection.switch = self

    @property
    def id(self):
        return "{}".format(self.dpid)

    def disconnect(self):
        """Disconnect the switch.

        """
        self.connection.close()
        self.connection = None
        log.info("Switch %s is disconnected", self.dpid)

    def get_interface_by_port_no(self, port_no):
        return self.interfaces.get(port_no)

    def is_active(self):
        return (now() - self.lastseen).seconds <= CONNECTION_TIMEOUT

    def is_connected(self):
        """Verifies if the switch is connected to a socket.
        """
        return self.connection.is_connected() and self.is_active()

    def update_connection(self, connection):
        self.connection = connection
        self.connection.switch = self

    def update_features(self, features):
        # TODO: We should avoid OF structs here
        self.features = features

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

    def update_interface(self, interface):
        if interface.port_number not in self.interfaces:
            self.interfaces[interface.port_number] = interface

    def update_mac_table(self, mac, port_number):
        if mac.value in self.mac2port:
            self.mac2port[mac.value].add(port_number)
        else:
            self.mac2port[mac.value] = set([port_number])

    def last_flood(self, ethernet_frame):
        """Returns the timestamp when the ethernet_frame was flooded.

        This method is usefull to check if a frame was flooded before or not.
        """
        try:
            return self.flood_table[ethernet_frame.get_hash()]
        except KeyError:
            return None

    def should_flood(self, ethernet_frame):
        last_flood = self.last_flood(ethernet_frame)

        if last_flood is None:
            return True
        elif (now() - last_flood).microseconds > FLOOD_TIMEOUT:
            return True
        else:
            return False

    def update_flood_table(self, ethernet_frame):
        self.flood_table[ethernet_frame.get_hash()] = now()

    def where_is_mac(self, mac):
        try:
            return list(self.mac2port[mac.value])
        except KeyError as exception:
            return None

    def as_dict(self):
        return {'id': self.id,
                'dpid': self.dpid,
                'ofp_version': self.ofp_version,
                'class': 'switch'}

    def as_json(self):
        return json.dumps(self.as_dict())
