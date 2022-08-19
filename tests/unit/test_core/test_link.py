"""Link tests."""
import logging
import time
import unittest
from unittest.mock import Mock, patch

from kytos.core.common import EntityStatus
from kytos.core.exceptions import KytosLinkCreationError
from kytos.core.interface import TAG, Interface, TAGType
from kytos.core.link import Link
from kytos.core.switch import Switch

logging.basicConfig(level=logging.CRITICAL)


# pylint: disable=protected-access,too-many-public-methods
class TestLink(unittest.TestCase):
    """Test Links."""

    def setUp(self):
        """Create interface objects."""
        self.switch1 = self._get_v0x04_switch('dpid1')
        self.iface1 = Interface('interface1', 41, self.switch1)
        self.switch2 = self._get_v0x04_switch('dpid2')
        self.iface2 = Interface('interface2', 42, self.switch2)

    @staticmethod
    def _get_v0x04_switch(name: str):
        """Create a v0x04 Switch"""
        switch = Switch(name)
        switch.connection = Mock()
        switch.connection.protocol.version = 0x04
        return switch

    def test__eq__(self):
        """Test __eq__ method."""
        link_1 = Link(self.iface1, self.iface2)
        link_2 = Link(self.iface2, self.iface1)

        iface3 = Interface('interface1', 1, self.switch1)
        iface4 = Interface('interface2', 2, self.switch2)

        link_3 = Link(iface3, iface4)

        self.assertTrue(link_1.__eq__(link_2))
        self.assertFalse(link_1.__eq__(link_3))

    def test__repr__(self):
        """Test __repr__ method."""
        link = Link(self.iface1, self.iface2)
        expected = ("Link(Interface('interface1', 41, Switch('dpid1')), "
                    "Interface('interface2', 42, Switch('dpid2')))")
        self.assertEqual(repr(link), expected)

    def test_id(self):
        """Test id property."""
        ids = []

        for value in [(self.switch1, 1, self.switch2, 2),
                      (self.switch2, 2, self.switch1, 1),
                      (self.switch1, 1, self.switch1, 2),
                      (self.switch1, 2, self.switch1, 1)]:
            iface1 = Interface('iface', value[1], value[0])
            iface2 = Interface('iface', value[3], value[2])
            link = Link(iface1, iface2)

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
        with self.assertRaises(KytosLinkCreationError):
            Link(self.iface1, None)

        with self.assertRaises(KytosLinkCreationError):
            Link(None, self.iface2)

    def test_link_id(self):
        """Test equality of links with the same values ​​in different order."""
        link1 = Link(self.iface1, self.iface2)
        link2 = Link(self.iface2, self.iface1)
        self.assertEqual(link1.id, link2.id)

    def test_status_funcs(self) -> None:
        """Test status_funcs."""
        # If it's enabled and active but a func returns DOWN, then DOWN
        Link.register_status_func("some_napp_some_func",
                                  lambda link: EntityStatus.DOWN)
        for intf in (self.iface1, self.iface2):
            intf.enable()
            intf.activate()
        link = Link(self.iface1, self.iface2)
        link.enable()
        link.activate()
        assert link.status == EntityStatus.DOWN

        # No changes in status if it returns None
        Link.register_status_func("some_napp_some_func",
                                  lambda link: None)
        assert link.status == EntityStatus.UP

        # If it's deactivated then it shouldn't be able to make it go UP
        link.deactivate()
        assert link.status == EntityStatus.DOWN
        Link.register_status_func("some_napp_some_func",
                                  lambda link: EntityStatus.UP)
        assert link.status == EntityStatus.DOWN
        link.activate()
        assert link.status == EntityStatus.UP

        # If it's disabled, then it shouldn't be considered DOWN
        link.disable()
        Link.register_status_func("some_napp_some_func",
                                  lambda link: EntityStatus.DOWN)
        assert link.status == EntityStatus.DISABLED

    def test_multiple_status_funcs(self) -> None:
        """Test multiple status_funcs."""
        # If it's enabled and active but a func returns DOWN, then DOWN
        Link.register_status_func("some_napp_some_func",
                                  lambda link: None)
        Link.register_status_func("some_napp_another_func",
                                  lambda link: EntityStatus.DOWN)
        for intf in (self.iface1, self.iface2):
            intf.enable()
            intf.activate()
        link = Link(self.iface1, self.iface2)
        link.enable()
        link.activate()
        assert link.status == EntityStatus.DOWN

        # It should be UP if the func no longer returns DOWN
        Link.register_status_func("some_napp_another_func",
                                  lambda link: None)
        assert link.status == EntityStatus.UP

    def test_available_tags(self):
        """Test available_tags property."""
        link = Link(self.iface1, self.iface2)
        tag_1 = Mock(tag_type=TAGType.VLAN)
        tag_2 = Mock(tag_type=TAGType.VLAN)
        tag_3 = Mock(tag_type=TAGType.VLAN_QINQ)
        tag_4 = Mock(tag_type=TAGType.MPLS)
        link.endpoint_a.available_tags = [tag_1, tag_2, tag_3, tag_4]
        link.endpoint_b.available_tags = [tag_2, tag_3, tag_4]

        self.assertEqual(link.available_tags, [tag_2, tag_3, tag_4])

    @patch('kytos.core.interface.Interface.is_tag_available')
    def test_use_tag__success(self, mock_is_tag_available):
        """Test use_tag method to success case."""
        mock_is_tag_available.side_effect = [True, True]
        link = Link(self.iface1, self.iface2)

        result = link.use_tag(Mock())
        self.assertTrue(result)

    @patch('kytos.core.interface.Interface.is_tag_available')
    def test_use_tag__error(self, mock_is_tag_available):
        """Test use_tag method to error case."""
        mock_is_tag_available.side_effect = [True, False]
        link = Link(self.iface1, self.iface2)

        result = link.use_tag(Mock())
        self.assertFalse(result)

    def test_make_tag_available__success(self):
        """Test make_tag_available method to success case."""
        link = Link(self.iface1, self.iface2)
        self.assertEqual(self.iface1.available_tags[-1],
                         self.iface2.available_tags[-1])
        tag = TAG(TAGType.VLAN, self.iface1.available_tags[-1].value + 1)
        result = link.make_tag_available(tag)
        self.assertTrue(result)

    def test_make_tag_available__error(self):
        """Test make_tag_available method to error case."""
        link = Link(self.iface1, self.iface2)
        result = link.make_tag_available(self.iface1.available_tags[0])
        self.assertFalse(result)

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

    def test_available_vlans(self):
        """Test available_vlans method."""
        link = Link(self.iface1, self.iface2)
        tag_1 = Mock(tag_type=TAGType.VLAN)
        tag_2 = Mock(tag_type=TAGType.VLAN)
        tag_3 = Mock(tag_type=TAGType.VLAN_QINQ)
        tag_4 = Mock(tag_type=TAGType.MPLS)
        link.endpoint_a.available_tags = [tag_1, tag_2, tag_3, tag_4]
        link.endpoint_b.available_tags = [tag_2, tag_3, tag_4]

        vlans = link.available_vlans()
        self.assertEqual(vlans, [tag_2])

    def test_get_available_vlans(self):
        """Test _get_available_vlans method."""
        link = Link(self.iface1, self.iface2)
        tag_1 = Mock(tag_type=TAGType.VLAN)
        tag_2 = Mock(tag_type=TAGType.VLAN_QINQ)
        tag_3 = Mock(tag_type=TAGType.MPLS)
        link.endpoint_a.available_tags = [tag_1, tag_2, tag_3]

        vlans = link._get_available_vlans(link.endpoint_a)
        self.assertEqual(vlans, [tag_1])
