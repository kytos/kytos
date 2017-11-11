"""Module with main classes related to Switches."""
import json
import logging

from pyof.v0x01.common.phy_port import PortFeatures as PortFeatures01
from pyof.v0x04.common.port import PortFeatures as PortFeatures04

from kytos.core.constants import CONNECTION_TIMEOUT, FLOOD_TIMEOUT
from kytos.core.helpers import now

__all__ = ('Interface', 'Switch')

LOG = logging.getLogger(__name__)


class Interface:  # pylint: disable=too-many-instance-attributes
    """Interface Class used to abstract the network interfaces."""

    # pylint: disable=too-many-arguments
    def __init__(self, name, port_number, switch, address=None, state=None,
                 features=None, speed=None):
        """Assign the parameters to instance attributes.

        Args:
            name (string): name from this interface.
            port_number (int): port number from this interface.
            switch (:class:`~.core.switch.Switch`): Switch with this interface.
            address (|hw_address|): Port address from this interface.
            state (|port_stats|): Port Stat from interface.
            features (|port_features|): Port feature used to calculate link
                utilization from this interface.
            speed (int, float): Interface speed in bytes per second. Defaults
                to what is informed by the switch. Return ``None`` if not set
                and switch does not inform the speed.
        """
        self.name = name
        self.port_number = int(port_number)
        self.switch = switch
        self.address = address
        self.state = state
        self.features = features
        self.nni = False
        self.endpoints = []
        self.stats = None
        self._custom_speed = speed

    def __eq__(self, other):
        """Compare Interface class with another instance."""
        if isinstance(other, str):
            return self.address == other
        elif isinstance(other, Interface):
            return self.port_number == other.port_number and \
                self.name == other.name and \
                self.address == other.address and \
                self.switch.dpid == other.switch.dpid
        return False

    @property
    def id(self):  # pylint: disable=invalid-name
        """Return id from Interface intance.

        Returns:
            string: Interface id.

        """
        return "{}:{}".format(self.switch.dpid, self.port_number)

    @property
    def uni(self):
        """Return if an interface is a user-to-network Interface."""
        return not self.nni

    def get_endpoint(self, endpoint):
        """Return a tuple with existent endpoint, None otherwise.

        Args:
            endpoint(|hw_address|, :class:`.Interface`): endpoint instance.

        Returns:
            tuple: A tuple with endpoint and time of last update.

        """
        for item in self.endpoints:
            if endpoint == item[0]:
                return item
        return None

    def add_endpoint(self, endpoint):
        """Create a new endpoint to Interface instance.

        Args:
            endpoint(|hw_address|, :class:`.Interface`): A target endpoint.
        """
        exists = self.get_endpoint(endpoint)
        if not exists:
            self.endpoints.append((endpoint, now()))

    def delete_endpoint(self, endpoint):
        """Delete a existent endpoint in Interface instance.

        Args:
            endpoint (|hw_address|, :class:`.Interface`): A target endpoint.
        """
        exists = self.get_endpoint(endpoint)
        if exists:
            self.endpoints.remove(exists)

    def update_endpoint(self, endpoint):
        """Update or create new endpoint to Interface instance.

        Args:
            endpoint(|hw_address|, :class:`.Interface`): A target endpoint.
        """
        exists = self.get_endpoint(endpoint)
        if exists:
            self.delete_endpoint(endpoint)
        self.add_endpoint(endpoint)

    @property
    def speed(self):
        """Return the link speed in bytes per second, None otherwise.

        If the switch was disconnected, we have :attr:`features` and speed is
        still returned for common values between v0x01 and v0x04. For specific
        v0x04 values (40 Gbps, 100 Gbps and 1 Tbps), the connection must be
        active so we can make sure the protocol version is v0x04.

        Returns:
            int, None: Link speed in bytes per second or ``None``.

        """
        if self._custom_speed is not None:
            return self._custom_speed
        return self.get_of_features_speed()

    def set_custom_speed(self, bytes_per_second):
        """Set a speed that overrides switch OpenFlow information.

        If ``None`` is given, :attr:`speed` becomes the one given by the
        switch.
        """
        self._custom_speed = bytes_per_second

    def get_custom_speed(self):
        """Return custom speed or ``None`` if not set."""
        return self._custom_speed

    def get_of_features_speed(self):
        """Return the link speed in bytes per second, None otherwise.

        If the switch was disconnected, we have :attr:`features` and speed is
        still returned for common values between v0x01 and v0x04. For specific
        v0x04 values (40 Gbps, 100 Gbps and 1 Tbps), the connection must be
        active so we can make sure the protocol version is v0x04.

        Returns:
            int, None: Link speed in bytes per second or ``None``.

        """
        speed = self._get_v0x01_v0x04_speed()
        # Don't use switch.is_connected() because we can have the protocol
        if speed is None and self._is_v0x04():
            speed = self._get_v0x04_speed()
        if speed is not None:
            return speed
        # Warn unknown speed
        # Use shorter switch ID with its beginning and end
        if isinstance(self.switch.id, str) and len(self.switch.id) > 20:
            switch_id = self.switch.id[:3] + '...' + self.switch.id[-3:]
        else:
            switch_id = self.switch.id
        LOG.warning("Couldn't get port %s speed, sw %s, feats %s",
                    self.port_number, switch_id, self.features)

    def _is_v0x04(self):
        """Whether the switch is connected using OpenFlow 1.3."""
        return self.switch.is_connected() and \
            self.switch.connection.protocol.version == 0x04

    def _get_v0x01_v0x04_speed(self):
        """Check against all values of v0x01. They're part of v0x04."""
        fts = self.features
        pfts = PortFeatures01
        if fts and fts & pfts.OFPPF_10GB_FD:
            return 10 * 10**9 / 8
        elif fts and fts & (pfts.OFPPF_1GB_HD | pfts.OFPPF_1GB_FD):
            return 10**9 / 8
        elif fts and fts & (pfts.OFPPF_100MB_HD | pfts.OFPPF_100MB_FD):
            return 100 * 10**6 / 8
        elif fts and fts & (pfts.OFPPF_10MB_HD | pfts.OFPPF_10MB_FD):
            return 10 * 10**6 / 8

    def _get_v0x04_speed(self):
        """Check against higher enums of v0x04.

        Must be called after :meth:`get_v0x01_speed` returns ``None``.
        """
        fts = self.features
        pfts = PortFeatures04
        if fts and fts & pfts.OFPPF_1TB_FD:
            return 10**12 / 8
        elif fts and fts & pfts.OFPPF_100GB_FD:
            return 100 * 10**9 / 8
        elif fts and fts & pfts.OFPPF_40GB_FD:
            return 40 * 10**9 / 8

    def get_hr_speed(self):
        """Return Human-Readable string for link speed.

        Returns:
            string: String with link speed. e.g: '350 Gbps' or '350 Mbps'.

        """
        speed = self.speed
        if speed is None:
            return ''
        speed *= 8
        if speed == 10**12:
            return '1 Tbps'
        if speed >= 10**9:
            return '{} Gbps'.format(round(speed / 10**9))
        return '{} Mbps'.format(round(speed / 10**6))

    def as_dict(self):
        """Return a dictionary with Interface attributes.

        Speed is in bytes/sec. Example of output (100 Gbps):

        .. code-block:: python3

            {'id': '00:00:00:00:00:00:00:01:2',
             'name': 'eth01',
             'port_number': 2,
             'mac': '00:7e:04:3b:c2:a6',
             'switch': '00:00:00:00:00:00:00:01',
             'type': 'interface',
             'nni': False,
             'uni': True,
             'speed': 12500000000}

        Returns:
            dict: Dictionary filled with interface attributes.

        """
        iface_dict = {'id': self.id,
                      'name': self.name,
                      'port_number': self.port_number,
                      'mac': self.address,
                      'switch': self.switch.dpid,
                      'type': 'interface',
                      'nni': self.nni,
                      'uni': self.uni,
                      'speed': self.speed}
        if self.stats:
            iface_dict['stats'] = self.stats.as_dict()
        return iface_dict

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
            string: Json filled with interface attributes.

        """
        return json.dumps(self.as_dict())


class Switch:
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

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-public-methods

    def __init__(self, dpid, connection=None, features=None):
        """Contructor of switches have the below parameters.

        Args:
          dpid (|DPID|): datapath_id of the switch
          connection (:class:`~.Connection`): Connection used by switch.
          features (|features_reply|): FeaturesReply instance.

        """
        self.dpid = dpid
        self.connection = connection
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

        Args:
            desc (|desc_stats|):
                Description Class with new values of switch's descriptions.
        """
        self.description['manufacturer'] = desc.mfr_desc.value
        self.description['hardware'] = desc.hw_desc.value
        self.description['software'] = desc.sw_desc.value
        self.description['serial'] = desc.serial_num.value
        self.description['data_path'] = desc.dp_desc.value

    @property
    def id(self):  # pylint: disable=invalid-name
        """Return id from Switch instance.

        Returns:
            string: the switch id is the data_path_id from switch.

        """
        return "{}".format(self.dpid)

    @property
    def ofp_version(self):
        """Return the OFP version of this switch."""
        if self.connection:
            return '0x0' + str(self.connection.protocol.version)
        return None

    def disconnect(self):
        """Disconnect the switch instance."""
        self.connection.close()
        self.connection = None
        LOG.info("Switch %s is disconnected", self.dpid)

    def get_interface_by_port_no(self, port_no):
        """Get interface by port number from Switch instance.

        Returns:
            :class:`~.core.switch.Interface`: Interface from specific port.

        """
        return self.interfaces.get(port_no)

    def get_flow_by_id(self, flow_id):
        """Return a Flow using the flow_id given. None if not found in flows.

        Args:
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

        Args:
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

        Args:
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

        Args:
            interface (:class:`~kytos.core.switch.Interface`):
                Interface object to be storeged.
        """
        self.interfaces[interface.port_number] = interface

    def remove_interface(self, interface):
        """Remove a interface from switch instance.

        Args:
            interface (:class:`~kytos.core.switch.Interface`):
                Interface object to be removed.
        """
        del self.interfaces[interface.port_number]

    def update_mac_table(self, mac, port_number):
        """Link the mac address with a port number.

        Args:
            mac (|hw_address|): mac address from switch.
            port (int): port linked in mac address.
        """
        if mac.value in self.mac2port:
            self.mac2port[mac.value].add(port_number)
        else:
            self.mac2port[mac.value] = set([port_number])

    def last_flood(self, ethernet_frame):
        """Return the timestamp when the ethernet_frame was flooded.

        This method is usefull to check if a frame was flooded before or not.

        Args:
            ethernet_frame (|ethernet|): Ethernet instance to be verified.

        Returns:
            datetime.datetime.now:
                Last time when the ethernet_frame was flooded.

        """
        try:
            return self.flood_table[ethernet_frame.get_hash()]
        except KeyError:
            return None

    def should_flood(self, ethernet_frame):
        """Verify if the ethernet frame should flood.

        Args:
            ethernet_frame (|ethernet|): Ethernet instance to be verified.

        Returns:
            bool: True if the ethernet_frame should flood.

        """
        last_flood = self.last_flood(ethernet_frame)
        diff = (now() - last_flood).microseconds

        return last_flood is None or diff > FLOOD_TIMEOUT

    def update_flood_table(self, ethernet_frame):
        """Update a flood table using the given ethernet frame.

        Args:
            ethernet_frame (|ethernet|): Ethernet frame to be updated.
        """
        self.flood_table[ethernet_frame.get_hash()] = now()

    def where_is_mac(self, mac):
        """Return all ports from specific mac address.

        Args:
            mac (|hw_address|): Mac address from switch.

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
            dict: Dictionary filled with interface attributes.

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
                'data_path': self.description.get('data_path', ''),
                'interfaces': {i.id: i.as_dict()
                               for i in self.interfaces.values()}}

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
            string: Json filled with switch'attributes.

        """
        return json.dumps(self.as_dict())
