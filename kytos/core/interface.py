"""Module with main classes related to Interfaces."""
import json
import logging
from enum import IntEnum

from pyof.v0x01.common.phy_port import Port as PortNo01
from pyof.v0x01.common.phy_port import PortFeatures as PortFeatures01
from pyof.v0x04.common.port import PortFeatures as PortFeatures04
from pyof.v0x04.common.port import PortNo as PortNo04

from kytos.core.common import GenericEntity
from kytos.core.helpers import now

__all__ = ('Interface',)

LOG = logging.getLogger(__name__)


class TAGType(IntEnum):
    """Class that represents a TAG Type."""

    VLAN = 1
    VLAN_QINQ = 2
    MPLS = 3


class TAG:
    """Class that represents a TAG."""

    def __init__(self, tag_type, value):
        self.tag_type = tag_type
        self.value = value

    def __eq__(self, other):
        return self.tag_type == other.tag_type and self.value == other.value

    def as_dict(self):
        """Return a dictionary representating a tag object."""
        return {'tag_type': self.tag_type, 'value': self.value}

    @classmethod
    def from_dict(cls, tag_dict):
        """Return a TAG instance from python dictionary."""
        return cls(tag_dict.get('tag_type'), tag_dict.get('value'))

    @classmethod
    def from_json(cls, tag_json):
        """Return a TAG instance from json."""
        return cls.from_dict(json.loads(tag_json))

    def as_json(self):
        """Return a json representating a tag object."""
        return json.dumps(self.as_dict())

    def __repr__(self):
        return f"TAG({self.tag_type!r}, {self.value!r})"


class Interface(GenericEntity):  # pylint: disable=too-many-instance-attributes
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
            state (|port_stats|): Port Stat from interface. It will be
            deprecated.
            features (|port_features|): Port feature used to calculate link
                utilization from this interface. It will be deprecated.
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
        self.link = None
        self._custom_speed = speed
        self.set_available_tags(range(1, 4096))

        super().__init__()

    def __repr__(self):
        return f"Interface('{self.name}', {self.port_number}, {self.switch!r})"

    def __eq__(self, other):
        """Compare Interface class with another instance."""
        if isinstance(other, str):
            return self.address == other
        if isinstance(other, Interface):
            return self.port_number == other.port_number and \
                self.switch.dpid == other.switch.dpid
        return False

    @property
    def id(self):  # pylint: disable=invalid-name
        """Return id from Interface instance.

        Returns:
            string: Interface id.

        """
        return "{}:{}".format(self.switch.dpid, self.port_number)

    @property
    def uni(self):
        """Return if an interface is a user-to-network Interface."""
        return not self.nni

    def set_available_tags(self, iterable):
        """Set a range of VLAN tags to be used by this Interface.

        Args:
            iterable ([int]): range of VLANs.
        """
        self.available_tags = []

        for i in iterable:
            vlan = TAGType.VLAN
            tag = TAG(vlan, i)
            self.available_tags.append(tag)

    def enable(self):
        """Enable this interface instance.

        Also enable the switch instance this interface is attached to.
        """
        self.switch.enable()
        self._enabled = True

    def use_tag(self, tag):
        """Remove a specific tag from available_tags if it is there.

        Return False in case the tag is already removed.
        """
        if tag in self.available_tags:
            self.available_tags.remove(tag)
            return True
        return False

    def is_tag_available(self, tag):
        """Check if a tag is available."""
        return tag in self.available_tags

    def get_next_available_tag(self):
        """Get the next available tag from the interface.

        Return the next available tag if exists and remove from the
        available tags.
        If no tag is available return False.
        """
        try:
            return self.available_tags.pop()
        except IndexError:
            return False

    def make_tag_available(self, tag):
        """Add a specific tag in available_tags."""
        if not self.is_tag_available(tag):
            self.available_tags.append(tag)
            return True
        return False

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

    def update_link(self, link):
        """Update link for this interface in a consistent way.

        Verify of the other endpoint of the link has the same Link information
        attached to it, and change it if necessary.

        Warning: This method can potentially change information of other
        Interface instances. Use it with caution.
        """
        if self not in (link.endpoint_a, link.endpoint_b):
            return False

        if self.link is None or self.link != link:
            self.link = link

        if link.endpoint_a == self:
            endpoint = link.endpoint_b
        else:
            endpoint = link.endpoint_a

        if endpoint.link is None or endpoint.link != link:
            endpoint.link = link

        return True

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

        if self._is_v0x04() and self.port_number == PortNo04.OFPP_LOCAL:
            return 0

        if not self._is_v0x04() and self.port_number == PortNo01.OFPP_LOCAL:
            return 0

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
        return None

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
        if fts and fts & (pfts.OFPPF_1GB_HD | pfts.OFPPF_1GB_FD):
            return 10**9 / 8
        if fts and fts & (pfts.OFPPF_100MB_HD | pfts.OFPPF_100MB_FD):
            return 100 * 10**6 / 8
        if fts and fts & (pfts.OFPPF_10MB_HD | pfts.OFPPF_10MB_FD):
            return 10 * 10**6 / 8
        return None

    def _get_v0x04_speed(self):
        """Check against higher enums of v0x04.

        Must be called after :meth:`get_v0x01_speed` returns ``None``.
        """
        fts = self.features
        pfts = PortFeatures04
        if fts and fts & pfts.OFPPF_1TB_FD:
            return 10**12 / 8
        if fts and fts & pfts.OFPPF_100GB_FD:
            return 100 * 10**9 / 8
        if fts and fts & pfts.OFPPF_40GB_FD:
            return 40 * 10**9 / 8
        return None

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
             'speed': 12500000000,
             'metadata': {},
             'active': True,
             'enabled': False,
             'link': ""
            }

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
                      'speed': self.speed,
                      'metadata': self.metadata,
                      'active': self.is_active(),
                      'enabled': self.is_enabled(),
                      'link': self.link.id if self.link else ""}
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


class UNI:
    """Class that represents an User-to-Network Interface."""

    def __init__(self, interface, user_tag=None):
        self.user_tag = user_tag
        self.interface = interface

    def __eq__(self, other):
        """Override the default implementation."""
        return (self.user_tag == other.user_tag and
                self.interface == other.interface)

    def is_valid(self):
        """Check if TAG is possible for this interface TAG pool."""
        if self.user_tag:
            return self.interface.is_tag_available(self.user_tag)
        return True

    def as_dict(self):
        """Return a dict representating a UNI object."""
        return {'interface_id': self.interface.id,
                'tag': self.user_tag.as_dict()}

    def as_json(self):
        """Return a json representating a UNI object."""
        return json.dumps(self.as_dict())


class NNI:
    """Class that represents an Network-to-Network Interface."""

    def __init__(self, interface):
        self.interface = interface


class VNNI(NNI):
    """Class that represents an Virtual Network-to-Network Interface."""

    def __init__(self, service_tag, *args, **kwargs):
        self.service_tag = service_tag

        super().__init__(*args, **kwargs)
