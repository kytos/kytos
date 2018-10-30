"""Link tests."""
import logging
import unittest
from unittest.mock import Mock

from kytos.core.interface import Interface
from kytos.core.link import Link
from kytos.core.switch import Switch

logging.basicConfig(level=logging.CRITICAL)


class TestLink(unittest.TestCase):
    """Test Links."""

    def setUp(self):
        """Create interface objects."""
        self.iface1, self.iface2 = self._get_v0x04_ifaces()

    @staticmethod
    def _get_v0x04_ifaces(*args, **kwargs):
        """Create a pair of v0x04 interfaces with optional extra arguments."""
        switch1 = Switch('dpid1')
        switch1.connection = Mock()
        switch1.connection.protocol.version = 0x04
        iface1 = Interface('interface1', 41, switch1, *args, **kwargs)

        switch2 = Switch('dpid2')
        switch2.connection = Mock()
        switch2.connection.protocol.version = 0x04
        iface2 = Interface('interface2', 42, switch2, *args, **kwargs)

        return iface1, iface2

    def test_init(self):
        """Test normal Link initialization."""
        link = Link(self.iface1, self.iface2)
        self.assertIsInstance(link, Link)
        self.assertIs(link.is_active(), True)
        self.assertIs(link.is_enabled(), False)

    def test_init_with_null_endpoints(self):
        """Test initialization with None as endpoints."""
        with self.assertRaises(ValueError):
            Link(None, None)
