"""Interface tests."""
import logging
import unittest
from unittest.mock import Mock

from pyof.v0x04.common.port import PortFeatures

from kytos.core.interface import Interface
from kytos.core.switch import Switch

logging.basicConfig(level=logging.CRITICAL)


class TestInterface(unittest.TestCase):
    """Test Interfaces."""

    def setUp(self):
        """Create interface object."""
        self.iface = self._get_v0x04_iface()

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
