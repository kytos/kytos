"""Interface tests."""
import logging
import unittest
from unittest.mock import MagicMock, Mock

from pyof.v0x04.common.port import PortFeatures

from kytos.core.interface import TAG, UNI, Interface, TAGType
from kytos.core.switch import Switch

logging.basicConfig(level=logging.CRITICAL)


class TestTAG(unittest.TestCase):
    """TAG tests."""

    def setUp(self):
        """Create TAG object."""
        self.tag = TAG(1, 123)

    def test_from_dict(self):
        """Test from_dict method."""
        tag_dict = {'tag_type': 2, 'value': 456}
        tag = self.tag.from_dict(tag_dict)

        self.assertEqual(tag.tag_type, 2)
        self.assertEqual(tag.value, 456)

    def test_as_dict(self):
        """Test as_dict method."""
        self.assertEqual(self.tag.as_dict(), {'tag_type': 1, 'value': 123})

    def test_from_json(self):
        """Test from_json method."""
        tag_json = '{"tag_type": 2, "value": 456}'
        tag = self.tag.from_json(tag_json)

        self.assertEqual(tag.tag_type, 2)
        self.assertEqual(tag.value, 456)

    def test_as_json(self):
        """Test as_json method."""
        self.assertEqual(self.tag.as_json(), '{"tag_type": 1, "value": 123}')

    def test__repr__(self):
        """Test __repr__ method."""
        self.assertEqual(repr(self.tag), 'TAG(<TAGType.VLAN: 1>, 123)')


# pylint: disable=protected-access, too-many-public-methods
class TestInterface(unittest.TestCase):
    """Test Interfaces."""

    def setUp(self):
        """Create interface object."""
        self.iface = self._get_v0x04_iface()

    def test_repr(self):
        """Test repr() output."""
        expected = "Interface('name', 42, Switch('dpid'))"
        self.assertEqual(repr(self.iface), expected)

    @staticmethod
    def _get_v0x04_iface(*args, **kwargs):
        """Create a v0x04 interface object with optional extra arguments."""
        switch = Switch('dpid')
        switch.connection = Mock()
        switch.connection.protocol.version = 0x04
        return Interface('name', 42, switch, *args, **kwargs)

    def test_speed_feature_none(self):
        """When port's current features is None."""
        self.iface.features = None
        self.assertIsNone(self.iface.speed)
        self.assertEqual('', self.iface.get_hr_speed())

    def test_speed_feature_zero(self):
        """When port's current features is 0. E.g. port 65534."""
        self.iface.features = 0
        self.assertIsNone(self.iface.speed)
        self.assertEqual('', self.iface.get_hr_speed())

    def test_1_tera_speed(self):
        """1Tb link."""
        self.iface.features = PortFeatures.OFPPF_1TB_FD
        self.assertEqual(10**12 / 8, self.iface.speed)
        self.assertEqual('1 Tbps', self.iface.get_hr_speed())

    def test_100_giga_speed(self):
        """100Gb link."""
        self.iface.features = PortFeatures.OFPPF_100GB_FD
        self.assertEqual(100 * 10**9 / 8, self.iface.speed)
        self.assertEqual('100 Gbps', self.iface.get_hr_speed())

    def test_40_giga_speed(self):
        """40Gb link."""
        self.iface.features = PortFeatures.OFPPF_40GB_FD
        self.assertEqual(40 * 10**9 / 8, self.iface.speed)
        self.assertEqual('40 Gbps', self.iface.get_hr_speed())

    def test_10_giga_speed(self):
        """10Gb link."""
        self.iface.features = PortFeatures.OFPPF_10GB_FD
        self.assertEqual(10 * 10**9 / 8, self.iface.speed)
        self.assertEqual('10 Gbps', self.iface.get_hr_speed())

    def test_1_giga_speed(self):
        """1Gb link."""
        self.iface.features = PortFeatures.OFPPF_1GB_FD
        self.assertEqual(10**9 / 8, self.iface.speed)
        self.assertEqual('1 Gbps', self.iface.get_hr_speed())

    def test_100_mega_speed(self):
        """100Mb link."""
        self.iface.features = PortFeatures.OFPPF_100MB_FD
        self.assertEqual(100 * 10**6 / 8, self.iface.speed)
        self.assertEqual('100 Mbps', self.iface.get_hr_speed())

    def test_10_mega_speed(self):
        """10Mb link."""
        self.iface.features = PortFeatures.OFPPF_10MB_FD
        self.assertEqual(10 * 10**6 / 8, self.iface.speed)
        self.assertEqual('10 Mbps', self.iface.get_hr_speed())

    def test_speed_setter(self):
        """Should return speed that was set and not features'."""
        expected_speed = 12345
        self.iface.set_custom_speed(expected_speed)
        actual_speed = self.iface.speed
        self.assertEqual(expected_speed, actual_speed)

    def test_speed_in_constructor(self):
        """Custom speed should override features'."""
        expected_speed = 6789
        iface = self._get_v0x04_iface(speed=expected_speed)
        self.assertEqual(expected_speed, iface.speed)

    def test_speed_removing_features(self):
        """Should return custom speed again when features becomes None."""
        custom_speed = 101112
        of_speed = 10 * 10**6 / 8
        iface = self._get_v0x04_iface(speed=custom_speed,
                                      features=PortFeatures.OFPPF_10MB_FD)
        self.assertEqual(of_speed, iface.speed)
        iface.features = None
        self.assertEqual(custom_speed, iface.speed)

    def test_interface_available_tags(self):
        """Test available_tags on Interface class."""
        default_range = list(range(1, 4096))
        intf_values = [tag.value for tag in self.iface.available_tags]
        self.assertListEqual(intf_values, default_range)

        custom_range = list(range(100, 199))
        self.iface.set_available_tags(custom_range)
        intf_values = [tag.value for tag in self.iface.available_tags]
        self.assertListEqual(intf_values, custom_range)

    def test_all_available_tags(self):
        """Test all available_tags on Interface class."""
        max_range = 4096

        for i in range(1, max_range):
            next_tag = self.iface.get_next_available_tag()
            self.assertIs(type(next_tag), TAG)
            self.assertEqual(next_tag.value, max_range - i)

        next_tag = self.iface.get_next_available_tag()
        self.assertEqual(next_tag, False)

    def test_interface_is_tag_available(self):
        """Test is_tag_available on Interface class."""
        max_range = 4096
        for i in range(1, max_range):
            tag = TAG(TAGType.VLAN, i)

            next_tag = self.iface.is_tag_available(tag)
            self.assertTrue(next_tag)

        # test lower limit
        tag = TAG(TAGType.VLAN, 0)
        self.assertFalse(self.iface.is_tag_available(tag))
        # test upper limit
        tag = TAG(TAGType.VLAN, max_range)
        self.assertFalse(self.iface.is_tag_available(tag))

    def test_interface_use_tags(self):
        """Test all use_tag on Interface class."""

        tag = TAG(TAGType.VLAN, 100)
        # check use tag for the first time
        is_success = self.iface.use_tag(tag)
        self.assertTrue(is_success)

        # check use tag for the second time
        is_success = self.iface.use_tag(tag)
        self.assertFalse(is_success)

        # check use tag after returning the tag to the pool
        self.iface.make_tag_available(tag)
        is_success = self.iface.use_tag(tag)
        self.assertTrue(is_success)

    def test_enable(self):
        """Test enable method."""
        self.iface.switch = MagicMock()

        self.iface.enable()

        self.iface.switch.enable.assert_called()
        self.assertTrue(self.iface._enabled)

    def test_get_endpoint(self):
        """Test get_endpoint method."""
        endpoint = ('endpoint', 'time')
        self.iface.endpoints = [endpoint]

        return_endpoint = self.iface.get_endpoint('endpoint')

        self.assertEqual(return_endpoint, endpoint)

    def test_add_endpoint(self):
        """Test add_endpoint method."""
        self.iface.add_endpoint('endpoint')

        self.assertEqual(len(self.iface.endpoints), 1)

    def test_delete_endpoint(self):
        """Test delete_endpoint method."""
        endpoint = ('endpoint', 'time')
        self.iface.endpoints = [endpoint]

        self.iface.delete_endpoint('endpoint')

        self.assertEqual(len(self.iface.endpoints), 0)

    def test_update_endpoint(self):
        """Test update_endpoint method."""
        endpoint = ('endpoint', 'time')
        self.iface.endpoints = [endpoint]

        self.iface.update_endpoint('endpoint')

        self.assertEqual(len(self.iface.endpoints), 1)

    def test_update_link__none(self):
        """Test update_link method when this interface is not in link
           endpoints."""
        link = MagicMock()
        link.endpoint_a = MagicMock()
        link.endpoint_b = MagicMock()

        result = self.iface.update_link(link)

        self.assertFalse(result)

    def test_update_link__endpoint_a(self):
        """Test update_link method when this interface is the endpoint a."""
        interface = MagicMock()
        interface.link = None
        link = MagicMock()
        link.endpoint_a = self.iface
        link.endpoint_b = interface

        self.iface.update_link(link)

        self.assertEqual(self.iface.link, link)
        self.assertEqual(interface.link, link)

    def test_update_link__endpoint_b(self):
        """Test update_link method when this interface is the endpoint b."""
        interface = MagicMock()
        interface.link = None
        link = MagicMock()
        link.endpoint_a = interface
        link.endpoint_b = self.iface

        self.iface.update_link(link)

        self.assertEqual(self.iface.link, link)
        self.assertEqual(interface.link, link)


class TestUNI(unittest.TestCase):
    """UNI tests."""

    def setUp(self):
        """Create UNI object."""
        switch = MagicMock()
        switch.dpid = '00:00:00:00:00:00:00:01'
        interface = Interface('name', 1, switch)
        user_tag = TAG(1, 123)
        self.uni = UNI(interface, user_tag)

    def test__eq__(self):
        """Test __eq__ method."""
        user_tag = TAG(2, 456)
        interface = Interface('name', 2, MagicMock())
        other = UNI(interface, user_tag)

        self.assertFalse(self.uni.__eq__(other))

    def test_is_valid(self):
        """Test is_valid method for a valid, invalid and none tag."""
        self.assertTrue(self.uni.is_valid())

        with self.assertRaises(ValueError):
            TAG(999999, 123)

        self.uni.user_tag = None
        self.assertTrue(self.uni.is_valid())

    def test_as_dict(self):
        """Test as_dict method."""
        expected_dict = {'interface_id': '00:00:00:00:00:00:00:01:1',
                         'tag': {'tag_type': 1, 'value': 123}}
        self.assertEqual(self.uni.as_dict(), expected_dict)

    def test_as_json(self):
        """Test as_json method."""
        expected_json = '{"interface_id": "00:00:00:00:00:00:00:01:1", ' + \
                        '"tag": {"tag_type": 1, "value": 123}}'
        self.assertEqual(self.uni.as_json(), expected_json)
