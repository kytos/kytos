"""Interface tests."""
import logging
import unittest

from pyof.v0x01.common.phy_port import PortFeatures

from kytos.core.switch import Interface, Switch

logging.basicConfig(level=logging.CRITICAL)


class TestInterface(unittest.TestCase):
    """Test Interfaces."""

    def setUp(self):
        """Create interface object."""
        switch = Switch('dpid')
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

    def test_10GB_speed(self):
        """10GB link."""
        self.iface.features = PortFeatures.OFPPF_10GB_FD
        self.assertEqual(10 * 10**9, self.iface.get_speed())
        self.assertEqual('10 Gbps', self.iface.get_hr_speed())

    def test_1GB_speed(self):
        """1GB link."""
        self.iface.features = PortFeatures.OFPPF_1GB_FD
        self.assertEqual(10**9, self.iface.get_speed())
        self.assertEqual('1 Gbps', self.iface.get_hr_speed())

    def test_100MB_speed(self):
        """100MB link."""
        self.iface.features = PortFeatures.OFPPF_100MB_FD
        self.assertEqual(100 * 10**6, self.iface.get_speed())
        self.assertEqual('100 Mbps', self.iface.get_hr_speed())

    def test_10MB_speed(self):
        """10MB link."""
        self.iface.features = PortFeatures.OFPPF_10MB_FD
        self.assertEqual(10 * 10**6, self.iface.get_speed())
        self.assertEqual('10 Mbps', self.iface.get_hr_speed())
