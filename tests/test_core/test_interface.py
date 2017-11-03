"""Interface tests."""
import logging
import unittest
from unittest.mock import Mock

from pyof.v0x04.common.port import PortFeatures

from kytos.core.switch import Interface, Switch

logging.basicConfig(level=logging.CRITICAL)


class TestInterface(unittest.TestCase):
    """Test Interfaces."""

    def setUp(self):
        """Create interface object."""
        switch = Switch('dpid')
        switch.connection = Mock()
        switch.connection.protocol.version = 0x04
        self.iface = Interface('name', 42, switch)

    def test_speed_feature_none(self):
        """When port's current features is None."""
        self.iface.features = None
        self.assertIsNone(self.iface.get_speed())
        self.assertEqual('', self.iface.get_hr_speed())

    def test_speed_feature_zero(self):
        """When port's current features is 0. E.g. port 65534."""
        self.iface.features = 0
        self.assertIsNone(self.iface.get_speed())
        self.assertEqual('', self.iface.get_hr_speed())

    def test_1_tera_speed(self):
        """1Tb link."""
        self.iface.features = PortFeatures.OFPPF_1TB_FD
        self.assertEqual(10**12 / 8, self.iface.get_speed())
        self.assertEqual('1 Tbps', self.iface.get_hr_speed())

    def test_100_giga_speed(self):
        """100Gb link."""
        self.iface.features = PortFeatures.OFPPF_100GB_FD
        self.assertEqual(100 * 10**9 / 8, self.iface.get_speed())
        self.assertEqual('100 Gbps', self.iface.get_hr_speed())

    def test_40_giga_speed(self):
        """40Gb link."""
        self.iface.features = PortFeatures.OFPPF_40GB_FD
        self.assertEqual(40 * 10**9 / 8, self.iface.get_speed())
        self.assertEqual('40 Gbps', self.iface.get_hr_speed())

    def test_10_giga_speed(self):
        """10Gb link."""
        self.iface.features = PortFeatures.OFPPF_10GB_FD
        self.assertEqual(10 * 10**9 / 8, self.iface.get_speed())
        self.assertEqual('10 Gbps', self.iface.get_hr_speed())

    def test_1_giga_speed(self):
        """1Gb link."""
        self.iface.features = PortFeatures.OFPPF_1GB_FD
        self.assertEqual(10**9 / 8, self.iface.get_speed())
        self.assertEqual('1 Gbps', self.iface.get_hr_speed())

    def test_100_mega_speed(self):
        """100Mb link."""
        self.iface.features = PortFeatures.OFPPF_100MB_FD
        self.assertEqual(100 * 10**6 / 8, self.iface.get_speed())
        self.assertEqual('100 Mbps', self.iface.get_hr_speed())

    def test_10_mega_speed(self):
        """10Mb link."""
        self.iface.features = PortFeatures.OFPPF_10MB_FD
        self.assertEqual(10 * 10**6 / 8, self.iface.get_speed())
        self.assertEqual('10 Mbps', self.iface.get_hr_speed())
