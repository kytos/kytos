"""Test kytos.core.switch module."""
import asyncio
from unittest import TestCase
from unittest.mock import Mock

from kytos.core import Controller
from kytos.core.config import KytosConfig
from kytos.core.interface import Interface
from kytos.core.switch import Switch


class TestSwitch(TestCase):
    """Switch tests."""

    def setUp(self):
        """Instantiate a controller."""

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        self.options = KytosConfig().options['daemon']
        self.controller = Controller(self.options, loop=self.loop)
        self.controller.log = Mock()

    def test_repr(self):
        """Test repr() output."""
        switch = Switch('some-dpid')
        self.assertEqual(repr(switch), "Switch('some-dpid')")

    def tearDown(self):
        """TearDown."""
        self.loop.close()

    def test_switch_vlan_pool_default(self):
        """Test default vlan_pool value."""
        self.assertEqual(self.options.vlan_pool, '{}')

    def test_switch_vlan_pool_options(self):
        """Test switch with the example from kytos.conf."""
        dpid = "00:00:00:00:00:00:00:01"
        vlan_pool_json = '{"00:00:00:00:00:00:00:01": ' \
                         + '{"1": [[1, 2], [5, 10]], "4": [[3, 4]]}}'
        switch = Switch(dpid)
        self.controller.switches[dpid] = switch
        self.options.vlan_pool = vlan_pool_json
        switch.connection = Mock()
        switch.connection.protocol.version = 0x04
        self.controller.get_switch_or_create(dpid, switch.connection)

        port_id = 1
        intf = self.controller.switches[dpid].interfaces[port_id]
        tag_values = [tag.value for tag in intf.available_tags]
        self.assertEqual(tag_values, [1, 5, 6, 7, 8, 9])

        port_id = 4
        intf = self.controller.switches[dpid].interfaces[port_id]
        tag_values = [tag.value for tag in intf.available_tags]
        self.assertEqual(tag_values, [3])

        # this port number doesn't exist yet.
        port_7 = 7
        intf = Interface("test", port_7, switch)
        # no attr filters, so should associate as it is
        self.controller.switches[dpid].update_interface(intf)
        intf_obj = self.controller.switches[dpid].interfaces[port_7]
        self.assertEqual(intf_obj, intf)
        # assert default vlan_pool range (1, 4096)
        tag_values = [tag.value for tag in intf_obj.available_tags]
        self.assertEqual(tag_values, list(range(1, 4096)))
