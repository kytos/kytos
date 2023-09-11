"""Test kytos.core.switch module."""
import json
from datetime import datetime, timezone
from socket import error as SocketError
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from kytos.core import Controller
from kytos.core.common import EntityStatus
from kytos.core.config import KytosConfig
from kytos.core.constants import FLOOD_TIMEOUT
from kytos.core.interface import Interface
from kytos.core.switch import Switch


def get_date():
    """Return date with FLOOD_TIMEOUT+1 microseconds."""
    return datetime(2000, 1, 1, 0, 0, 0, FLOOD_TIMEOUT+1)


# pylint: disable=protected-access, too-many-public-methods
class TestSwitch(TestCase):
    """Switch tests."""

    def setUp(self):
        """Instantiate a controller."""

        self.options = KytosConfig().options['daemon']
        self.controller = Controller(self.options)
        self.controller.log = Mock()
        self.controller._buffers = MagicMock()
        self.switch = self.create_switch()

    @staticmethod
    def create_switch():
        """Create a new switch."""
        connection = MagicMock()
        connection.address = 'addr'
        connection.port = 'port'
        connection.protocol.version = 0x04
        switch = Switch('00:00:00:00:00:00:00:01', connection)
        switch._enabled = True
        switch.update_lastseen()
        return switch

    def test_repr(self):
        """Test repr() output."""
        expected_repr = "Switch('00:00:00:00:00:00:00:01')"
        self.assertEqual(repr(self.switch), expected_repr)

    def test_id(self):
        """Test id property."""
        self.assertEqual(self.switch.id, '00:00:00:00:00:00:00:01')

    def test_ofp_version(self):
        """Test ofp_version property."""
        self.assertEqual(self.switch.ofp_version, '0x04')

    def test_ofp_version__none(self):
        """Test ofp_version property when connection is none."""
        self.switch.connection = None
        self.assertIsNone(self.switch.ofp_version)

    def test_update_description(self):
        """Test update_description method."""
        desc = MagicMock()
        desc.mfr_desc.value = 'mfr_desc'
        desc.hw_desc.value = 'hw_desc'
        desc.sw_desc.value = 'sw_desc'
        desc.serial_num.value = 'serial_num'
        desc.dp_desc.value = 'dp_desc'

        self.switch.update_description(desc)

        self.assertEqual(self.switch.description['manufacturer'], 'mfr_desc')
        self.assertEqual(self.switch.description['hardware'], 'hw_desc')
        self.assertEqual(self.switch.description['software'], 'sw_desc')
        self.assertEqual(self.switch.description['serial'], 'serial_num')
        self.assertEqual(self.switch.description['data_path'], 'dp_desc')

    def test_disable(self):
        """Test disable method."""
        intf = MagicMock()
        self.switch.interfaces = {"1": intf}

        self.switch.disable()

        intf.disable.assert_called()
        self.assertFalse(self.switch._enabled)

    def test_disconnect(self):
        """Test disconnect method."""
        self.switch.disconnect()

        self.assertIsNone(self.switch.connection)

    def test_get_interface_by_port_no(self):
        """Test get_interface_by_port_no method."""
        interface_1 = MagicMock(port_number='1')
        interface_2 = MagicMock(port_number='2')
        self.switch.interfaces = {'1': interface_1, '2': interface_2}

        expected_interface_1 = self.switch.get_interface_by_port_no('1')
        expected_interface_2 = self.switch.get_interface_by_port_no('3')

        self.assertEqual(expected_interface_1, interface_1)
        self.assertIsNone(expected_interface_2)

    def test_update_or_create_interface_case1(self):
        """Test update_or_create_interface method."""
        interface_1 = Interface(name='interface_2', port_number=2,
                                switch=self.switch)
        self.switch.interfaces = {2: interface_1}

        self.switch.update_or_create_interface(2, name='new_interface_2')
        self.assertEqual(self.switch.interfaces[2].name, 'new_interface_2')

    def test_update_or_create_interface_case2(self):
        """Test update_or_create_interface method."""
        interface_1 = Interface(name='interface_2', port_number=2,
                                switch=self.switch)
        self.switch.interfaces = {2: interface_1}

        self.switch.update_or_create_interface(3, name='new_interface_3')
        self.assertEqual(self.switch.interfaces[2].name, 'interface_2')
        self.assertEqual(self.switch.interfaces[3].name, 'new_interface_3')

    def test_update_or_create_interface_case3(self):
        """Test update_or_create_interface method."""
        interface_1 = Interface(name='interface_2', port_number=2,
                                switch=self.switch)
        self.switch.interfaces = {2: interface_1}

        self.switch.update_or_create_interface(3, name='new_interface_3')
        self.assertEqual(self.switch.interfaces[2].name, 'interface_2')
        self.assertEqual(self.switch.interfaces[3].name, 'new_interface_3')

    def test_get_flow_by_id(self):
        """Test get_flow_by_id method."""
        flow_1 = MagicMock(id='1')
        flow_2 = MagicMock(id='2')
        self.switch.flows = [flow_1, flow_2]

        expected_flow_1 = self.switch.get_flow_by_id('1')
        expected_flow_2 = self.switch.get_flow_by_id('3')

        self.assertEqual(expected_flow_1, flow_1)
        self.assertIsNone(expected_flow_2)

    def test_is_connected__true(self):
        """Test is_connected method."""
        connection = MagicMock()
        connection.is_alive.return_value = True
        connection.is_established.return_value = True
        self.switch.connection = connection

        self.assertTrue(self.switch.is_connected())

    def test_is_connected__not_connection(self):
        """Test is_connected method when connection does not exist."""
        self.switch.connection = None

        self.assertFalse(self.switch.is_connected())

    def test_is_connected__not_alive(self):
        """Test is_connected method when switch has connection timeout."""
        connection = MagicMock()
        connection.is_alive.return_value = True
        connection.is_established.return_value = True
        self.switch.connection = connection
        self.switch.lastseen = datetime(1, 1, 1, 0, 0, 0, 0, timezone.utc)

        self.assertFalse(self.switch.is_connected())

    def test_is_active(self):
        """Test is_active method."""
        self.switch.is_connected = MagicMock()
        self.switch.is_connected.return_value = True
        self.assertTrue(self.switch.is_active())
        self.switch.is_connected.return_value = False
        self.assertFalse(self.switch.is_active())

    def test_update_connection(self):
        """Test update_connection method."""
        connection = MagicMock()
        self.switch.update_connection(connection)

        self.assertEqual(self.switch.connection, connection)
        self.assertEqual(self.switch.connection.switch, self.switch)

    def test_update_features(self):
        """Test update_features method."""
        self.switch.update_features('features')

        self.assertEqual(self.switch.features, 'features')

    def test_send(self):
        """Test send method."""
        self.switch.send('buffer')

        self.switch.connection.send.assert_called_with('buffer')

    def test_send_error(self):
        """Test send method to error case."""
        self.switch.connection.send.side_effect = SocketError

        with self.assertRaises(SocketError):
            self.switch.send(b'data')

    @patch('kytos.core.switch.now', return_value=get_date())
    def test_update_lastseen(self, mock_now):
        """Test update_lastseen method."""
        self.switch.update_lastseen()

        self.assertEqual(self.switch.lastseen, mock_now.return_value)

    def test_update_interface(self):
        """Test update_interface method."""
        interface = MagicMock(port_number=1)
        self.switch.update_interface(interface)

        self.assertEqual(self.switch.interfaces[1], interface)

    def test_remove_interface(self):
        """Test remove_interface method."""
        intf = MagicMock(port_number=1)
        self.switch.interfaces[1] = intf

        self.switch.remove_interface(intf)

        self.assertEqual(self.switch.interfaces, {})

    def test_update_mac_table(self):
        """Test update_mac_table method."""
        mac = MagicMock(value='00:00:00:00:00:00')
        self.switch.update_mac_table(mac, 1)
        self.switch.update_mac_table(mac, 2)

        self.assertEqual(self.switch.mac2port[mac.value], {1, 2})

    def test_last_flood(self):
        """Test last_flood method."""
        self.switch.flood_table['hash'] = 'timestamp'
        ethernet_frame = MagicMock()
        ethernet_frame.get_hash.return_value = 'hash'

        last_flood = self.switch.last_flood(ethernet_frame)

        self.assertEqual(last_flood, 'timestamp')

    def test_last_flood__error(self):
        """Test last_flood method to error case."""
        ethernet_frame = MagicMock()
        ethernet_frame.get_hash.return_value = 'hash'

        last_flood = self.switch.last_flood(ethernet_frame)

        self.assertIsNone(last_flood)

    @patch('kytos.core.switch.now', return_value=get_date())
    def test_should_flood(self, _):
        """Test should_flood method."""
        self.switch.flood_table['hash1'] = datetime(2000, 1, 1, 0, 0, 0, 0)
        self.switch.flood_table['hash2'] = datetime(2000, 1, 1, 0, 0, 0,
                                                    FLOOD_TIMEOUT)

        ethernet_frame = MagicMock()
        ethernet_frame.get_hash.side_effect = ['hash1', 'hash2']

        should_flood_1 = self.switch.should_flood(ethernet_frame)
        should_flood_2 = self.switch.should_flood(ethernet_frame)

        self.assertTrue(should_flood_1)
        self.assertFalse(should_flood_2)

    @patch('kytos.core.switch.now', return_value=get_date())
    def test_update_flood_table(self, mock_now):
        """Test update_flood_table method."""
        ethernet_frame = MagicMock()
        ethernet_frame.get_hash.return_value = 'hash'

        self.switch.update_flood_table(ethernet_frame)

        self.assertEqual(self.switch.flood_table['hash'],
                         mock_now.return_value)

    def test_where_is_mac(self):
        """Test where_is_mac method."""
        mac = MagicMock(value='00:00:00:00:00:00')

        expected_ports_1 = self.switch.where_is_mac(mac)

        self.switch.mac2port['00:00:00:00:00:00'] = set([1, 2, 3])
        expected_ports_2 = self.switch.where_is_mac(mac)

        self.assertIsNone(expected_ports_1)
        self.assertEqual(expected_ports_2, [1, 2, 3])

    def test_as_dict_as_json(self):
        """Test as_dict and as_json method."""
        expected_dict = {
            'id': '00:00:00:00:00:00:00:01',
            'name': '00:00:00:00:00:00:00:01',
            'dpid': '00:00:00:00:00:00:00:01',
            'connection': 'addr:port',
            'ofp_version': '0x04',
            'type': 'switch',
            'manufacturer': '',
            'serial': '',
            'hardware': '',
            'software': None,
            'data_path': '',
            'interfaces': {},
            'metadata': {},
            'active': True,
            'enabled': True,
            'status': 'UP',
            'status_reason': []
        }
        self.assertEqual(self.switch.as_dict(), expected_dict)

        expected_json = json.dumps(expected_dict)

        self.assertEqual(self.switch.as_json(), expected_json)

    def test_switch_initial_lastseen(self):
        """Test lastseen attribute initialization."""
        connection = MagicMock()
        connection.protocol.version = 0x04
        switch = Switch('00:00:00:00:00:00:00:01', connection)
        self.assertEqual(switch.is_active(), False)
        self.assertEqual(switch.lastseen,
                         datetime(1, 1, 1, 0, 0, 0, 0, timezone.utc))

    def test_status_funcs(self) -> None:
        """Test status_funcs."""
        self.switch.enable()
        self.switch.activate()
        assert self.switch.is_active()
        Switch.register_status_func(
            "some_napp_some_func",
            lambda switch: EntityStatus.DOWN
        )
        Switch.register_status_reason_func(
            "some_napp_some_func",
            lambda iface: {'test_status'}
        )
        assert self.switch.status == EntityStatus.DOWN
        assert self.switch.status_reason == {'test_status'}
        Switch.register_status_func(
            "some_napp_some_func",
            lambda iface: None
        )
        Switch.register_status_reason_func(
            "some_napp_some_func",
            lambda iface: set()
        )
        assert self.switch.status == EntityStatus.UP
        assert self.switch.status_reason == set()
