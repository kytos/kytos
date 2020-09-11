"""Test kytos.lib.helpers module."""
import asyncio
from unittest import TestCase
from unittest.mock import MagicMock

from kytos.core.controller import Controller
from kytos.lib.helpers import (get_connection_mock, get_controller_mock,
                               get_interface_mock, get_kytos_event_mock,
                               get_link_mock, get_switch_mock, get_test_client)


class TestHelpers(TestCase):
    """Test the helpers methods."""

    def test_controller_mock(self):
        """Test controller mock."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        controller = get_controller_mock(loop)

        self.assertEqual(type(controller), Controller)

    def test_interface_mock(self):
        """Test interface mock."""
        switch = MagicMock()
        switch.dpid = "00:00:00:00:00:00:00:01"
        interface_mock = get_interface_mock('name', 123, switch)

        self.assertEqual(interface_mock.id, '00:00:00:00:00:00:00:01:123')
        self.assertEqual(interface_mock.name, 'name')
        self.assertEqual(interface_mock.port_number, 123)
        self.assertEqual(interface_mock.switch, switch)
        self.assertEqual(interface_mock.address, '00:00:00:00:00:00')
        self.assertTrue(interface_mock.lldp)

    def test_link_mock(self):
        """Test link mock."""
        endpoint_a = MagicMock()
        endpoint_b = MagicMock()
        link_mock = get_link_mock(endpoint_a, endpoint_b)

        self.assertEqual(link_mock.endpoint_a, endpoint_a)
        self.assertEqual(link_mock.endpoint_b, endpoint_b)
        self.assertEqual(link_mock.metadata, {"A": 0, "BB": 0.0,
                                              "CCC": "test"})

    def test_switch_mock(self):
        """Test switch mock."""
        dpid = "00:00:00:00:00:00:00:01"
        switch_mock = get_switch_mock(dpid, 0x04)

        self.assertEqual(switch_mock.dpid, dpid)
        self.assertEqual(switch_mock.ofp_version, '0x04')
        self.assertEqual(switch_mock.connection.protocol.version, 0x04)
        self.assertEqual(switch_mock.connection.switch, switch_mock)
        self.assertEqual(switch_mock.connection.address, '00:00:00:00:00:00')
        self.assertEqual(switch_mock.connection.state.value, 0)

    def test_connection_mock(self):
        """Test connection mock."""
        switch = MagicMock()
        connection_mock = get_connection_mock(0x04, switch, 'addr', 123)

        self.assertEqual(connection_mock.protocol.version, 0x04)
        self.assertEqual(connection_mock.switch, switch)
        self.assertEqual(connection_mock.address, 'addr')
        self.assertEqual(connection_mock.state, 123)

    def test_kytos_event_mock(self):
        """Test kytos_event mock."""
        kytos_event_mock = get_kytos_event_mock(name='event',
                                                content={'message': 'msg',
                                                         'destination': 'dest',
                                                         'source': 'src'})
        self.assertEqual(kytos_event_mock.name, 'event')
        self.assertEqual(kytos_event_mock.message, 'msg')
        self.assertEqual(kytos_event_mock.destination, 'dest')
        self.assertEqual(kytos_event_mock.source, 'src')

    def test_get_test_client(self):
        """Test get_test_client method."""
        napp = MagicMock()

        api_server = MagicMock()
        api_server.app.test_client.return_value = 'client'

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        controller = get_controller_mock(loop)
        controller.api_server = api_server

        test_client = get_test_client(controller, napp)

        api_server.register_napp_endpoints.assert_called_with(napp)
        self.assertEqual(test_client, 'client')
