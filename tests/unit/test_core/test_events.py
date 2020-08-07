"""Test kytos.core.events module."""
from unittest import TestCase

from kytos.core.events import KytosEvent


class TestKytosEvent(TestCase):
    """KytosEvent tests."""

    def setUp(self):
        """Instantiate a KytosEvent."""
        self.event = KytosEvent('kytos/core.any')

    def test__str__(self):
        """Test __str__ method."""
        self.assertEqual(str(self.event), 'kytos/core.any')

    def test__repr__(self):
        """Test __repr__ method."""
        self.event.content = {"destination": "dest",
                              "source": "src",
                              "message": "msg"}
        expected = "KytosEvent('kytos/core.any', {'destination': 'dest', " + \
                   "'source': 'src', 'message': 'msg'})"

        self.assertEqual(repr(self.event), expected)

    def test_destination(self):
        """Test destination property and set_destination method."""
        self.assertEqual(self.event.destination, None)

        self.event.set_destination('dest')
        self.assertEqual(self.event.destination, 'dest')

    def test_source(self):
        """Test source property and set_source method."""
        self.assertEqual(self.event.source, None)

        self.event.set_source('src')
        self.assertEqual(self.event.source, 'src')

    def test_message(self):
        """Test message property."""
        self.assertEqual(self.event.message, None)

        self.event.content = {"message": "msg"}
        self.assertEqual(self.event.message, 'msg')
