"""Interface tests."""
import logging
import unittest
from unittest.mock import Mock

from pyof.v0x04.common.port import PortFeatures

from kytos.core.interface import TAG, Interface, TAGType
from kytos.core.switch import Switch

logging.basicConfig(level=logging.CRITICAL)


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
        self.iface.features = PortFeatures.OFPPF_10MB_FD
        self.iface.set_custom_speed(expected_speed)
        actual_speed = self.iface.speed
        self.assertEqual(expected_speed, actual_speed)

    def test_speed_in_constructor(self):
        """Custom speed should override features'."""
        expected_speed = 6789
        iface = self._get_v0x04_iface(speed=expected_speed,
                                      features=PortFeatures.OFPPF_10MB_FD)
        actual_speed = iface.speed
        self.assertEqual(expected_speed, actual_speed)

    def test_remove_custom_speed(self):
        """Should return features' speed again when custom's becomes None."""
        custom_speed = 101112
        of_speed = 10 * 10**6 / 8
        iface = self._get_v0x04_iface(speed=custom_speed,
                                      features=PortFeatures.OFPPF_10MB_FD)
        self.assertEqual(custom_speed, iface.speed)
        iface.set_custom_speed(None)
        self.assertEqual(of_speed, iface.speed)

    def test_interface_available_tags(self):
        """Test available_tags on Interface class."""
        default_range = [vlan for vlan in range(1, 4096)]
        intf_values = [tag.value for tag in self.iface.available_tags]
        self.assertListEqual(intf_values, default_range)

        custom_range = [vlan for vlan in range(100, 199)]
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
