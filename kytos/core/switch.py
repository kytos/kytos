"""Module with main classes related to Switches."""
import json
import logging

from pyof.v0x01.common.phy_port import PortFeatures

from kytos.core.constants import CONNECTION_TIMEOUT, FLOOD_TIMEOUT
from kytos.core.helpers import now

__all__ = ('Interface', 'Switch')

log = logging.getLogger(__name__)


class Interface(object):
    """Interface Class used to abstract the network interfaces."""

    def __init__(self, name, port_number, switch, address=None, state=None,
                 features=None):
        """The contructor of Interface have the below parameters.

        Parameters:
            name (string): name from this interface.
            port_number (int): port number from this interface.
            switch (:class:`~.core.switch.Switch`): Switch with this interface.
            address (HWAddress): Port address from this interface.
            state (PortState): Port Stat from interface.
            features (PortFeatures): Port feature used to calculate link
                                     utilization from this interface.
        """
        self.name = name
        self.port_number = int(port_number)
        self.switch = switch
        self.address = address
        self.state = state
        self.features = features
        self.endpoints = []

    def __eq__(self, other):
        """Method used to compare Interface class with another instance."""
        if isinstance(other, str):
            return self.address == other
        elif isinstance(other, Interface):
            return self.port_number == other.port_number and \
                self.name == other.name and \
                self.address == other.address and \
                self.switch.dpid == other.switch.dpid
        return False

    @property
    def id(self):
        """Return id from Interface intance.

        Returns:
            string: Interface id.
        """
        return "{}:{}".format(self.switch.dpid, self.port_number)

    def get_endpoint(self, endpoint):
        """Return a tuple with existent endpoint, None otherwise.

        Parameters:
            endpoint (HWAddress,Interface): endpoint instance.

        Returns:
            item (tuple): A tuple with endpoint and time of last update.
        """
        for item in self.endpoints:
            if endpoint == item[0]:
                return item
        return None

    def is_link_between_switches(self):
        """Return True if instance is link between switches.False otherwise."""
        for endpoint, _ in self.endpoints:
            if isinstance(endpoint, Interface):
                return True
        return False

    def add_endpoint(self, endpoint):
        """Create a new endpoint to Interface instance.

        Parameters:
            endpoint (HWAddress): A target endpoint.
        """
        exists = self.get_endpoint(endpoint)
        if not exists:
            self.endpoints.append((endpoint, now()))

    def delete_endpoint(self, endpoint):
        """Delete a existent endpoint in Interface instance.

        Parameters:
            endpoint (HWAddress): A target endpoint.
        """
        exists = self.get_endpoint(endpoint)
        if exists:
            self.endpoints.remove(exists)

    def update_endpoint(self, endpoint):
        """Update or create new endpoint to Interface instance.

        Parameters:
            endpoint (HWAddress): A target endpoint.
        """
        exists = self.get_endpoint(endpoint)
        if exists:
            self.delete_endpoint(endpoint)
        self.add_endpoint(endpoint)

    def get_speed(self):
        """Return the link speed in bits per second, None otherwise.

        Returns:
            speed (int): Link speed in bits per second.
        """
        fs = self.features
        PF = PortFeatures
        if fs and fs & PF.OFPPF_10GB_FD:
            return 10 * 10**9
        elif fs and fs & (PF.OFPPF_1GB_HD | PF.OFPPF_1GB_FD):
            return 10**9
        elif fs and fs & (PF.OFPPF_100MB_HD | PF.OFPPF_100MB_FD):
            return 100 * 10**6
        elif fs and fs & (PF.OFPPF_10MB_HD | PF.OFPPF_10MB_FD):
            return 10 * 10**6
        else:
            log.warning("No speed port %s, sw %s, feats %s", self.port_number,
                        self.switch.dpid[-3:], self.features)
        return None

    def get_hr_speed(self):
        """Return Human-Readable string for link speed.

        Returns:
            human_speed (string): String with link speed.
            e.g: '350 Gbps' or '350 Mbps'.
        """
        speed = self.get_speed()
        if speed is None:
            return ''
        elif speed >= 10**9:
            return '{} Gbps'.format(round(speed / 10**9))
        return '{} Mbps'.format(round(speed / 10**6))

    def as_dict(self):
        """Return a dictionary with Interface attributes.

        Example of output:

        .. code-block:: python3

            {'id': '00:00:00:00:00:00:00:01:2',
             'name': 'eth01',
             'port_number': 2,
             'mac': '00:7e:04:3b:c2:a6',
             'switch': '00:00:00:00:00:00:00:01',
             'type': 'interface',
             'speed': '350 Mbps'}

        Returns:
            dictionary (dict): Dictionary filled with interface attributes.
        """
        return {'id': self.id,
                'name': self.name,
                'port_number': self.port_number,
                'mac': self.address,
                'switch': self.switch.dpid,
                'type': 'interface',
                'speed': self.get_hr_speed()}

    def as_json(self):
        """Return a json with Interfaces attributes.

        Example of output:

        .. code-block:: json

            {"mac": "00:7e:04:3b:c2:a6",
             "switch": "00:00:00:00:00:00:00:01",
             "type": "interface",
             "name": "eth01",
             "id": "00:00:00:00:00:00:00:01:2",
             "port_number": 2,
             "speed": "350 Mbps"}

        Returns:
            json (string): Json filled with interface attributes.
        """
        return json.dumps(self.as_dict())


class Switch(object):
    """Switch class is a abstraction from switches.

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
    """

    def __init__(self, dpid, connection=None, ofp_version='0x01',
                 features=None):
        """Contructor of switches have the below parameters.

        Parameters:
            dpid (DPID): datapath_id of the switch
            connection (:class:`~.core.switch.Connection`):
                Connection used by switch.
            ofp_version (string): Current talked OpenFlow version.
            features (FeaturesReply): FeaturesReply instance.
        """
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
        #:     the last flood.
        self.flood_table = {}
        self.interfaces = {}
        self.flows = []
        self.description = {}

        if connection:
            connection.switch = self

    def update_description(self, desc):
        """Update switch'descriptions from Switch instance.

        Parameters:
            desc (DescStats):
                Description Class with new values of switch'descriptions.
        """
        self.description['manufacturer'] = desc.mfr_desc.value
        self.description['hardware'] = desc.hw_desc.value
        self.description['software'] = desc.sw_desc.value
        self.description['serial'] = desc.serial_num.value
        self.description['data_path'] = desc.dp_desc.value

    @property
    def id(self):
        """Return id from Switch instance.

        Returns:
            string: the switch id is the data_path_id from switch.
        """
        return "{}".format(self.dpid)

    def disconnect(self):
        """Disconnect the switch instance."""
        self.connection.close()
        self.connection = None
        log.info("Switch %s is disconnected", self.dpid)

    def get_interface_by_port_no(self, port_no):
        """Get interface by port number from Switch instance.

        Returns:
            interface (:class:`~.core.switch.Interface`):
                Interface from specific port.
        """
        return self.interfaces.get(port_no)

    def get_flow_by_id(self, flow_id):
        """Return a Flow using the flow_id given. None if not found in flows.

        Parameters:
            flow_id (int): identifier from specific flow stored.
        """
        for flow in self.flows:
            if flow_id == flow.id:
                return flow
        return None

    def is_active(self):
        """Return true if the switch connection is alive."""
        return (now() - self.lastseen).seconds <= CONNECTION_TIMEOUT

    def is_connected(self):
        """Verify if the switch is connected to a socket."""
        return (self.connection is not None and
                self.connection.is_alive() and
                self.connection.is_established() and self.is_active())

    def update_connection(self, connection):
        """Update switch connection.

        Parameters:
            connection (:class:`~.core.switch.Connection`):
                New connection to this instance of switch.
        """
        self.connection = connection
        self.connection.switch = self

    def update_features(self, features):
        """Update :attr:`features` attribute."""
        self.features = features

    def send(self, buffer):
        """Send a buffer data to the real switch.

        Parameters:
          buffer (bytes): bytes to be sent to the switch throught its
                            connection.
        """
        if self.connection:
            self.connection.send(buffer)

    def update_lastseen(self):
        """Update the lastseen attribute."""
        self.lastseen = now()

    def update_interface(self, interface):
        """Update a interface from switch instance.

        Parameters:
            interface (:class:`~kytos.core.switch.Interface`):
                Interface object to be storeged.
        """
        if interface.port_number not in self.interfaces:
            self.interfaces[interface.port_number] = interface

    def update_mac_table(self, mac, port_number):
        """Link the mac address with a port number.

        Parameters:
            mac (HWAddress): mac address from switch.
            port (int): port linked in mac address.
        """
        if mac.value in self.mac2port:
            self.mac2port[mac.value].add(port_number)
        else:
            self.mac2port[mac.value] = set([port_number])

    def last_flood(self, ethernet_frame):
        """Return the timestamp when the ethernet_frame was flooded.

        This method is usefull to check if a frame was flooded before or not.
        """
        try:
            return self.flood_table[ethernet_frame.get_hash()]
        except KeyError:
            return None

    def should_flood(self, ethernet_frame):
        """Verify if the ethernet frame should flood.

        Parameters:
            ethernet_frame (Ethernet): Ethernet instance to be verified.
        Returns:
            shoudl_flood (bool): True if the ethernet_frame should flood.
        """
        last_flood = self.last_flood(ethernet_frame)
        diff = (now() - last_flood).microseconds

        return last_flood is None or diff > FLOOD_TIMEOUT

    def update_flood_table(self, ethernet_frame):
        """Update a flood table using the given ethernet frame.

        Parameters:
            ethernet_frame (Ethernet): Ethernet frame to be updated.
        """
        self.flood_table[ethernet_frame.get_hash()] = now()

    def where_is_mac(self, mac):
        """"Return all ports from specific mac address.

        Parameters:
            mac (HWAddress): Mac address from switch.
        Returns:
            :class:`list`: A list of ports. None otherswise.
        """
        try:
            return list(self.mac2port[mac.value])
        except KeyError:
            return None

    def as_dict(self):
        """Return a dictionary with switch attributes.

        Example of output:

        .. code-block:: python3

               {'id': '00:00:00:00:00:00:00:03:2',
                'name': '00:00:00:00:00:00:00:03:2',
                'dpid': '00:00:00:00:03',
                'connection':  connection,
                'ofp_version': '0x01',
                'type': 'switch',
                'manufacturer': "",
                'serial': "",
                'hardware': "Open vSwitch",
                'software': 2.5,
                'data_path': ""
                }


        Returns:
            dictionary (dict): Dictionary filled with interface attributes.
        """
        connection = ""
        if self.connection is not None:
            address = self.connection.address
            port = self.connection.port
            connection = "{}:{}".format(address, port)

        return {'id': self.id,
                'name': self.id,
                'dpid': self.dpid,
                'connection': connection,
                'ofp_version': self.ofp_version,
                'type': 'switch',
                'manufacturer': self.description.get('manufacturer', ''),
                'serial': self.description.get('serial', ''),
                'hardware': self.description.get('hardware', ''),
                'software': self.description.get('software'),
                'data_path': self.description.get('data_path', '')}

    def as_json(self):
        """Return a json with switch'attributes.

        Example of output:

        .. code-block:: json

            {"data_path": "",
             "hardware": "Open vSwitch",
             "dpid": "00:00:00:00:03",
             "name": "00:00:00:00:00:00:00:03:2",
             "manufacturer": "",
             "serial": "",
             "software": 2.5,
             "id": "00:00:00:00:00:00:00:03:2",
             "ofp_version": "0x01",
             "type": "switch",
             "connection": ""}

        Returns:
            json (string): Json filled with switch'attributes.
        """
        return json.dumps(self.as_dict())
