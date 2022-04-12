"""Module with Kytos Events."""
import json
from datetime import datetime
from uuid import uuid4

from kytos.core.helpers import now


class KytosEvent:
    """Base Event class.

    The event data will be passed in the `content` attribute, which should be a
    dictionary.
    """

    def __init__(self, name=None, content=None):
        """Create an event to be published.

        Args:
            name (string): The name of the event. You should prepend it with
                           the name of the napp.
            content (dict): Dictionary with any extra data for the event.
        """
        self.name = name
        self.content = content if content is not None else {}
        self.timestamp = now()
        self.reinjections = 0

        # pylint: disable=invalid-name
        self.id = uuid4()
        # pylint: enable=invalid-name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"KytosEvent({self.name!r}, {self.content!r})"

    def as_dict(self):
        """Return KytosEvent as a dict."""
        return {'id': str(self.id), 'name': self.name, 'content': self.content,
                'timestamp': self.timestamp, 'reinjections': self.reinjections}

    def as_json(self):
        """Return KytosEvent as json."""
        as_dict = self.as_dict()
        timestamp = datetime.strftime(as_dict['timestamp'],
                                      '%Y-%m-%dT%H:%M:%S')
        as_dict['timestamp'] = timestamp
        try:
            return json.dumps(as_dict)
        except TypeError:
            as_dict['content'] = str(as_dict['content'])
            return json.dumps(as_dict)

    @property
    def destination(self):
        """Return the destination of KytosEvent."""
        return self.content.get('destination')

    def set_destination(self, destination):
        """Update the destination of KytosEvent.

        Args:
            destination (string): destination of KytosEvent.
        """
        self.content['destination'] = destination

    @property
    def source(self):
        """Return the source of KytosEvent."""
        return self.content.get('source')

    def set_source(self, source):
        """Update the source of KytosEvent.

        Args:
            source (string): source of KytosEvent.
        """
        self.content['source'] = source

    @property
    def message(self):
        """Return the message carried by the event if it exists.

        If there is any OpenFlow message on the event it'll be stored on
        the 'message' key of the 'content' attribute.

        Returns:
            A python-openflow message instance if it exists, None otherwise.

        """
        try:
            return self.content['message']
        except KeyError:
            return None
