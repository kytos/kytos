"""Link tests."""
import logging
import time
from unittest.mock import Mock

import pytest

from kytos.core.common import EntityStatus
from kytos.core.exceptions import KytosLinkCreationError
from kytos.core.interface import Interface, TAGType
from kytos.core.link import Link
from kytos.core.switch import Switch

logging.basicConfig(level=logging.CRITICAL)


# pylint: disable=protected-access,too-many-public-methods
# pylint: disable=attribute-defined-outside-init
class TestLink():
    """Test Links."""

    def setup_method(self):
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

        assert link_1 == link_2
        assert (link_1 == link_3) is False

    def test__repr__(self):
        """Test __repr__ method."""
        link = Link(self.iface1, self.iface2)
        expected = ("Link(Interface('interface1', 41, Switch('dpid1')), "
                    "Interface('interface2', 42, Switch('dpid2')), "
                    f"{link.id})")
        assert repr(link) == expected

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

        assert ids[0] == ids[1]
        assert ids[2] == ids[3]
        assert ids[0] != ids[2]

    def test_init(self):
        """Test normal Link initialization."""
        link = Link(self.iface1, self.iface2)
        assert isinstance(link, Link)
        assert link.is_active()
        assert link.is_enabled() is False

    def test_init_with_null_endpoints(self):
        """Test initialization with None as endpoints."""
        with pytest.raises(KytosLinkCreationError):
            Link(self.iface1, None)

        with pytest.raises(KytosLinkCreationError):
            Link(None, self.iface2)

    def test_link_id(self):
        """Test equality of links with the same values in different order."""
        link1 = Link(self.iface1, self.iface2)
        link2 = Link(self.iface2, self.iface1)
        assert link1.id == link2.id

    def test_status_funcs(self) -> None:
        """Test status_funcs."""
        # If it's enabled and active but a func returns DOWN, then DOWN
        Link.register_status_func(
            "some_napp_some_func",
            lambda link: EntityStatus.DOWN
        )
        Link.register_status_reason_func(
            "some_napp_some_func",
            lambda link: {'test_status'}
        )
        for intf in (self.iface1, self.iface2):
            intf.enable()
            intf.activate()
        link = Link(self.iface1, self.iface2)
        link.enable()
        link.activate()
        assert link.status == EntityStatus.DOWN
        assert link.status_reason == {'test_status'}

        # No changes in status if it returns None
        Link.register_status_func(
            "some_napp_some_func",
            lambda link: None
        )
        Link.register_status_reason_func(
            "some_napp_some_func",
            lambda link: set()
        )
        assert link.status == EntityStatus.UP
        assert link.status_reason == set()

        # If it's deactivated then it shouldn't be able to make it go UP
        link.deactivate()
        assert link.status == EntityStatus.DOWN
        Link.register_status_func(
            "some_napp_some_func",
            lambda link: EntityStatus.UP
        )
        Link.register_status_reason_func(
            "some_napp_some_func",
            lambda link: set()
        )
        assert link.status == EntityStatus.DOWN
        assert link.status_reason == {'deactivated'}
        link.activate()
        assert link.status == EntityStatus.UP
        assert link.status_reason == set()

        # If it's disabled, then it shouldn't be considered DOWN
        link.disable()
        Link.register_status_func(
            "some_napp_some_func",
            lambda link: EntityStatus.DOWN
        )
        Link.register_status_reason_func(
            "some_napp_some_func",
            lambda link: {'test_status'}
        )
        assert link.status == EntityStatus.DISABLED
        assert link.status_reason == {'test_status', 'disabled'}

    def test_multiple_status_funcs(self) -> None:
        """Test multiple status_funcs."""
        # If it's enabled and active but a func returns DOWN, then DOWN
        Link.register_status_func(
            "some_napp_some_func",
            lambda link: None
        )
        Link.register_status_reason_func(
            'some_napp_some_func',
            lambda link: set()
        )
        Link.register_status_func(
            "some_napp_another_func",
            lambda link: EntityStatus.DOWN
        )
        Link.register_status_reason_func(
            'some_napp_another_func',
            lambda link: {'test_status2'}
        )
        for intf in (self.iface1, self.iface2):
            intf.enable()
            intf.activate()
        link = Link(self.iface1, self.iface2)
        link.enable()
        link.activate()
        assert link.status == EntityStatus.DOWN
        assert link.status_reason == {'test_status2'}

        # It should be UP if the func no longer returns DOWN
        Link.register_status_func(
            "some_napp_another_func",
            lambda link: None
        )
        Link.register_status_reason_func(
            'some_napp_another_func',
            lambda link: set()
        )
        assert link.status == EntityStatus.UP
        assert link.status_reason == set()

    def test_available_tags(self):
        """Test available_tags property."""
        link = Link(self.iface1, self.iface2)
        link.endpoint_a.available_tags['vlan'] = [[1, 100]]
        link.endpoint_b.available_tags['vlan'] = [[50, 200]]

        vlans = link.available_tags()
        assert vlans == [[50, 100]]

    def test_get_next_available_tag(self, controller):
        """Test get next available tags returns different tags"""
        link = Link(self.iface1, self.iface2)
        tag = link.get_next_available_tag(controller, "link_id")
        next_tag = link.get_next_available_tag(controller, "link_id")

        assert tag != next_tag

    def test_get_tag_multiple_calls(self, controller):
        """Test get next available tags returns different tags"""
        link = Link(self.iface1, self.iface2)
        tag = link.get_next_available_tag(controller, "link_id")
        next_tag = link.get_next_available_tag(controller, "link_id")
        assert next_tag != tag

    def test_tag_life_cicle(self, controller):
        """Test get next available tags returns different tags"""
        link = Link(self.iface1, self.iface2)
        tag = link.get_next_available_tag(controller, "link_id")

        is_available = link.is_tag_available(tag)
        assert is_available is False

        link.make_tags_available(controller, tag, "link_id")
        is_available = link.is_tag_available(tag)
        assert is_available

    def test_concurrent_get_next_tag(self, controller):
        """Test get next available tags in concurrent execution"""
        # pylint: disable=import-outside-toplevel
        from tests.helper import test_concurrently
        _link = Link(self.iface1, self.iface2)

        _i = []
        available_tags = _link.endpoint_a.available_tags['vlan']
        _initial_size = 0
        for i, j in available_tags:
            _initial_size += j - i + 1

        @test_concurrently(20)
        def test_get_next_available_tag(controller):
            """Assert that get_next_available_tag() returns different tags."""
            _i.append(1)
            tag = _link.get_next_available_tag(controller, "link_id")
            time.sleep(0.0001)

            next_tag = _link.get_next_available_tag(controller, "link_id")

            assert tag != next_tag

        test_get_next_available_tag(controller)

        # sleep not needed because test_concurrently waits for all threads
        # to finish before returning.
        # time.sleep(0.1)

        # Check if after the 20th iteration we have 40 tags
        # It happens because we get 2 tags for every iteration
        available_tags = _link.endpoint_a.available_tags['vlan']
        _final_size = 0
        for i, j in available_tags:
            _final_size += j - i + 1
        assert _initial_size == _final_size + 40

    def test_available_vlans(self):
        """Test available_vlans method."""
        link = Link(self.iface1, self.iface2)
        link.endpoint_a.available_tags[TAGType.MPLS.value] = [[1, 100]]
        link.endpoint_b.available_tags[TAGType.MPLS.value] = [[50, 200]]

        vlans = link.available_vlans()
        assert vlans == [TAGType.VLAN.value]

    def test_get_available_vlans(self):
        """Test _get_available_vlans method."""
        link = Link(self.iface1, self.iface2)
        link.endpoint_a.available_tags[TAGType.VLAN_QINQ.value] = [[1, 1]]
        link.endpoint_a.available_tags[TAGType.MPLS.value] = [[1, 1]]
        vlans = link._get_available_vlans(link.endpoint_a)
        assert vlans == [TAGType.VLAN.value]
