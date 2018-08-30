"""Module with all classes related to links.

Links are low level abstractions representing connections between two
interfaces.
"""

import json
from uuid import uuid4

from kytos.core.common import GenericEntity
from kytos.core.interface import TAGType


class Link(GenericEntity):
    """Define a link between two Endpoints."""

    def __init__(self, endpoint_a, endpoint_b):
        """Create a Link instance and set its attributes."""
        self.endpoint_a = endpoint_a
        self.endpoint_b = endpoint_b
        self._uuid = uuid4()
        super().__init__()

    def is_enabled(self):
        """Override the is_enabled method.

        We consider a link enabled whether all the interfaces are enabled.

        Returns:
            boolean: True if the interfaces are enabled, othewrise False.

        """
        return (self._enabled and self.endpoint_a.is_enabled() and
                self.endpoint_b.is_enabled())

    def is_active(self):
        """Override the is_active method.

        We consider a link active whether all the interfaces are active.

        Returns:
            boolean: True if the interfaces are active, othewrise False.

        """
        return (self._active and self.endpoint_a.is_active() and
                self.endpoint_b.is_active())

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
            return True
        return False

    def available_vlans(self):
        """Get all available vlans from each interface in the link."""
        vlans_a = self._get_available_vlans(self.endpoint_a)
        vlans_b = self._get_available_vlans(self.endpoint_a)
        return [vlan for vlan in vlans_a if vlan in vlans_b]

    @staticmethod
    def _get_available_vlans(endpoint):
        """Return all vlans from endpoint."""
        tags = endpoint.available_tags
        return [tag for tag in tags if tag.tag_type == TAGType.VLAN]

    def as_dict(self):
        """Return the Link as a dictionary."""
        return {'id': self.id,
                'endpoint_a': self.endpoint_a.as_dict(),
                'endpoint_b': self.endpoint_b.as_dict(),
                'metadata': self.get_metadata_as_dict(),
                'active': self.is_active(),
                'enabled': self.is_enabled()}

    def as_json(self):
        """Return the Link as a JSON string."""
        return json.dumps(self.as_dict())
