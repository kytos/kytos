"""Test kytos.core.events module."""
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import UUID

from kytos.core.events import KytosEvent


class TestKytosEvent:
    """KytosEvent tests."""

    def setup_method(self):
        """Instantiate a KytosEvent."""
        self.event = KytosEvent('kytos/core.any')

    def test__str__(self):
        """Test __str__ method."""
        assert str(self.event) == 'kytos/core.any'

    def test__repr__(self):
        """Test __repr__ method."""
        self.event.content = {"destination": "dest",
                              "source": "src",
                              "message": "msg"}
        expected = "KytosEvent('kytos/core.any', {'destination': 'dest', " + \
                   "'source': 'src', 'message': 'msg'}, 0)"

        assert repr(self.event) == expected

    @staticmethod
    def test__lt__():
        """test less than operator."""
        event_a = KytosEvent('a', priority=5)
        event_b = KytosEvent('b', priority=-10)
        assert event_b < event_a

        event_a = KytosEvent('a')
        event_b = KytosEvent('b')
        assert event_a < event_b

    def test_destination(self):
        """Test destination property and set_destination method."""
        assert self.event.destination is None

        self.event.set_destination('dest')
        assert self.event.destination == 'dest'

    def test_source(self):
        """Test source property and set_source method."""
        assert self.event.source is None

        self.event.set_source('src')
        assert self.event.source == 'src'

    def test_message(self):
        """Test message property."""
        assert self.event.message is None

        self.event.content = {"message": "msg"}
        assert self.event.message == 'msg'

    def test_init_attrs(self):
        """Test init attrs."""
        assert self.event.name == "kytos/core.any"
        assert self.event.content == {}
        assert self.event.timestamp <= datetime.now(timezone.utc)
        assert self.event.id and isinstance(self.event.id, UUID)
        assert self.event.reinjections == 0
        assert self.event.priority == 0

    def test_trace_parent(self):
        """Test trace_parent."""
        parent = MagicMock()
        event = KytosEvent('kytos/core.any', trace_parent=parent)
        assert event.trace_parent == parent

    def test_as_dict(self):
        """Test as_dict."""
        expected = {'content': {}, 'id': str(self.event.id),
                    'name': 'kytos/core.any', 'reinjections': 0,
                    'timestamp': self.event.timestamp}
        assert self.event.as_dict() == expected

    def test_as_json(self):
        """Test as_json."""
        timestamp = datetime.strftime(self.event.timestamp,
                                      '%Y-%m-%dT%H:%M:%S')
        expected = {'content': {}, 'id': str(self.event.id),
                    'name': 'kytos/core.any', 'reinjections': 0,
                    'timestamp': timestamp}
        assert json.loads(self.event.as_json()) == expected
