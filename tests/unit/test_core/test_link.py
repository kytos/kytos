"""Link tests."""
import logging
import time
import unittest
from unittest.mock import Mock

from kytos.core.interface import Interface
from kytos.core.link import Link
from kytos.core.switch import Switch

logging.basicConfig(level=logging.CRITICAL)


# pylint: disable=protected-access
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

    def test__eq__(self):
        """Test __eq__ method."""
        link_1 = Link(self.iface1, self.iface2)
        link_2 = Link(self.iface2, self.iface1)

        iface1, iface2 = self._get_v0x04_ifaces()
        iface1.port_number = 1
        iface2.port_number = 2
        link_3 = Link(iface1, iface2)

        self.assertTrue(link_1.__eq__(link_2))
        self.assertFalse(link_1.__eq__(link_3))

    def test_id(self):
        """Test id property."""
        link = Link(self.iface1, self.iface2)
        ids = []

        for value in [('A', 1, 'B', 2), ('B', 2, 'A', 1), ('A', 1, 'A', 2),
                      ('A', 2, 'A', 1)]:
            link.endpoint_a.switch.dpid = value[0]
            link.endpoint_a.port_number = value[1]
            link.endpoint_b.switch.dpid = value[2]
            link.endpoint_b.port_number = value[3]

            ids.append(link.id)

        self.assertEqual(ids[0], ids[1])
        self.assertEqual(ids[2], ids[3])
        self.assertNotEqual(ids[0], ids[2])

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

    def test_link_id(self):
        """Test equality of links with the same values ​​in different order."""
        link1 = Link(self.iface1, self.iface2)
        link2 = Link(self.iface2, self.iface1)
        self.assertEqual(link1.id, link2.id)

    def test_get_next_available_tag(self):
        """Test get next available tags returns different tags"""
        link = Link(self.iface1, self.iface2)
        tag = link.get_next_available_tag()
        next_tag = link.get_next_available_tag()

        self.assertNotEqual(tag, next_tag)

    def test_get_tag_multiple_calls(self):
        """Test get next available tags returns different tags"""
        link = Link(self.iface1, self.iface2)
        tag = link.get_next_available_tag()
        next_tag = link.get_next_available_tag()
        self.assertNotEqual(next_tag.value, tag.value)

    def test_next_tag_with_use_tags(self):
        """Test get next availabe tags returns different tags"""
        link = Link(self.iface1, self.iface2)
        tag = link.get_next_available_tag()
        is_available = link.is_tag_available(tag)
        self.assertFalse(is_available)
        link.use_tag(tag)

    def test_tag_life_cicle(self):
        """Test get next available tags returns different tags"""
        link = Link(self.iface1, self.iface2)
        tag = link.get_next_available_tag()

        is_available = link.is_tag_available(tag)
        self.assertFalse(is_available)

        link.make_tag_available(tag)
        is_available = link.is_tag_available(tag)
        self.assertTrue(is_available)

    def test_concurrent_get_next_tag(self):
        """Test get next available tags in concurrent execution"""
        # pylint: disable=import-outside-toplevel
        from tests.helper import test_concurrently
        _link = Link(self.iface1, self.iface2)

        _i = []
        _initial_size = len(_link.endpoint_a.available_tags)

        @test_concurrently(20)
        def test_get_next_available_tag():
            """Assert that get_next_available_tag() returns different tags."""
            _i.append(1)
            _i_len = len(_i)
            tag = _link.get_next_available_tag()
            time.sleep(0.0001)
            _link.use_tag(tag)

            next_tag = _link.get_next_available_tag()
            _link.use_tag(next_tag)

            self.assertNotEqual(tag, next_tag)

        test_get_next_available_tag()

        # sleep not needed because test_concurrently waits for all threads
        # to finish before returning.
        # time.sleep(0.1)

        # Check if after the 20th iteration we have 40 tags
        # It happens because we get 2 tags for every iteration
        self.assertEqual(_initial_size,
                         len(_link.endpoint_a.available_tags) + 40)

    def test_get_available_vlans(self):
        """Test _get_available_vlans method."""
        link = Link(self.iface1, self.iface2)

        vlans = link._get_available_vlans(link.endpoint_a)
        self.assertEqual(len(vlans), 4095)
