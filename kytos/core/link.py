"""Module with all classes related to links.

Links are low level abstractions representing connections between two
interfaces.
"""

import json
from uuid import uuid4

from kytos.core.common import GenericEntity


class Link(GenericEntity):
    """Define a link between two Endpoints."""

    def __init__(self, endpoint_a, endpoint_b):
        """Create a Link instance and set its attributes."""
        self.endpoint_a = endpoint_a
        self.endpoint_b = endpoint_b
        self._uuid = uuid4()
        super().__init__()

    def __eq__(self, other):
        """Check if two instances of Link are equal."""
        return ((self.endpoint_a == other.endpoint_a and
                 self.endpoint_b == other.endpoint_b) or
                (self.endpoint_a == other.endpoint_b and
                 self.endpoint_b == other.endpoint_a))

    @property
    def id(self):  # pylint: disable=invalid-name
        """Return id from Link intance.

        Returns:
            string: link id.

        """
        return "{}".format(self._uuid)

    @property
    def available_tags(self):
        """Return the available tags for the link.

        Based on the endpoint tags.
        """
        return [tag for tag in self.endpoint_a.available_tags if tag in
                self.endpoint_b.available_tags]

    def enable(self):
        """Enable this link instance.

        Also enable the link's interfaces and the switches they're attached to.
        """
        self.endpoint_a.enable()
        self.endpoint_b.enable()
        self.enabled = True

    def use_tag(self, tag):
        """Remove a specific tag from available_tags if it is there."""
        if self.is_tag_available(tag):
            self.endpoint_a.use_tag(tag)
            self.endpoint_b.use_tag(tag)
            return True
        return False

    def is_tag_available(self, tag):
        """Check if a tag is available."""
        return (self.endpoint_a.is_tag_available(tag) and
                self.endpoint_b.is_tag_available(tag))

    def get_next_available_tag(self):
        """Return the next available tag if exists."""
        for tag in self.endpoint_a.available_tags:
            if tag in self.endpoint_b.available_tags:
                return tag
        return False

    def make_tag_available(self, tag):
        """Add a specific tag in available_tags."""
        if not self.is_tag_available(tag):
            self.endpoint_a.make_tag_available(tag)
            self.endpoint_b.make_tag_available(tag)
        else:
            return False

    def as_dict(self):
        """Return the Link as a dictionary."""
        return {'id': self.id,
                'endpoint_a': self.endpoint_a.as_dict(),
                'endpoint_b': self.endpoint_b.as_dict(),
                'metadata': self.metadata,
                'active': self.active,
                'enabled': self.enabled}

    def as_json(self):
        """Return the Link as a JSON string."""
        return json.dumps(self.as_dict())
