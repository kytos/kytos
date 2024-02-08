"""Test kytos.lib.helpers module."""
from unittest.mock import MagicMock

from httpx import AsyncClient

from kytos.core.controller import Controller
from kytos.lib.helpers import (get_connection_mock, get_controller_mock,
                               get_interface_mock, get_kytos_event_mock,
                               get_link_mock, get_switch_mock, get_test_client)


class TestHelpers:
    """Test the helpers methods."""

    def test_controller_mock(self):
        """Test controller mock."""
        controller = get_controller_mock()
        assert isinstance(controller, Controller)

    def test_interface_mock(self):
        """Test interface mock."""
        switch = MagicMock()
        switch.dpid = "00:00:00:00:00:00:00:01"
        interface_mock = get_interface_mock('name', 123, switch)

        assert interface_mock.id == '00:00:00:00:00:00:00:01:123'
        assert interface_mock.name == 'name'
        assert interface_mock.port_number == 123
        assert interface_mock.switch == switch
        assert interface_mock.address == '00:00:00:00:00:00'
        assert interface_mock.lldp

    def test_link_mock(self):
        """Test link mock."""
        endpoint_a = MagicMock()
        endpoint_b = MagicMock()
        link_mock = get_link_mock(endpoint_a, endpoint_b)

        assert link_mock.endpoint_a == endpoint_a
        assert link_mock.endpoint_b == endpoint_b
        assert link_mock.metadata == {"A": 0, "BB": 0.0, "CCC": "test"}

    def test_switch_mock(self):
        """Test switch mock."""
        dpid = "00:00:00:00:00:00:00:01"
        switch_mock = get_switch_mock(dpid, 0x04)

        assert switch_mock.dpid == dpid
        assert switch_mock.ofp_version == '0x04'
        assert switch_mock.connection.protocol.version == 0x04
        assert switch_mock.connection.switch == switch_mock
        assert switch_mock.connection.address == '00:00:00:00:00:00'
        assert switch_mock.connection.state.value == 0

    def test_connection_mock(self):
        """Test connection mock."""
        switch = MagicMock()
        connection_mock = get_connection_mock(0x04, switch, 'addr', 123)

        assert connection_mock.protocol.version == 0x04
        assert connection_mock.switch == switch
        assert connection_mock.address == 'addr'
        assert connection_mock.state == 123

    def test_kytos_event_mock(self):
        """Test kytos_event mock."""
        kytos_event_mock = get_kytos_event_mock(name='event',
                                                content={'message': 'msg',
                                                         'destination': 'dest',
                                                         'source': 'src'})
        assert kytos_event_mock.name == 'event'
        assert kytos_event_mock.message == 'msg'
        assert kytos_event_mock.destination == 'dest'
        assert kytos_event_mock.source == 'src'

    def test_get_test_client(self):
        """Test get_test_client method."""
        napp = MagicMock()

        api_server = MagicMock()
        controller = get_controller_mock()
        controller.api_server = api_server

        test_client = get_test_client(controller, napp)

        api_server.register_napp_endpoints.assert_called_with(napp)
        assert isinstance(test_client, AsyncClient)
