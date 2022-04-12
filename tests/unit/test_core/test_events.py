"""Test kytos.core.events module."""
import json
from datetime import datetime, timezone
from unittest import TestCase
from uuid import UUID

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

    def test_init_attrs(self):
        """Test init attrs."""
        assert self.event.name == "kytos/core.any"
        assert self.event.content == {}
        assert self.event.timestamp <= datetime.now(timezone.utc)
        assert self.event.id and isinstance(self.event.id, UUID)
        assert self.event.reinjections == 0

    def test_as_dict(self):
        """Test as_dict."""
        expected = {'content': {}, 'id': str(self.event.id),
                    'name': 'kytos/core.any', 'reinjections': 0,
                    'timestamp': self.event.timestamp}
        self.assertDictEqual(self.event.as_dict(), expected)

    def test_as_json(self):
        """Test as_json."""
        ts = datetime.strftime(self.event.timestamp, '%Y-%m-%dT%H:%M:%S')
        expected = {'content': {}, 'id': str(self.event.id),
                    'name': 'kytos/core.any', 'reinjections': 0,
                    'timestamp': ts}
        self.assertDictEqual(json.loads(self.event.as_json()), expected)

