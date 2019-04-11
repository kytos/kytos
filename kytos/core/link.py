"""Module with all classes related to links.

Links are low level abstractions representing connections between two
interfaces.
"""

import hashlib
import json

from kytos.core.common import GenericEntity
from kytos.core.interface import TAGType


class Link(GenericEntity):
    """Define a link between two Endpoints."""

    def __init__(self, endpoint_a, endpoint_b):
        """Create a Link instance and set its attributes.

        Two kytos.core.interface.Interface are required as parameters.
        """
        if endpoint_a is None:
            raise ValueError("endpoint_a cannot be None")
        if endpoint_b is None:
            raise ValueError("endpoint_b cannot be None")
        self.endpoint_a = endpoint_a
        self.endpoint_b = endpoint_b
        super().__init__()

    def __hash__(self):
        return hash(self.id)

    def is_enabled(self):
        """Override the is_enabled method.

        We consider a link enabled when all the interfaces are enabled.

        Returns:
            boolean: True if both interfaces are enabled, False otherwise.

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
        return self.id == other.id

    @property
    def id(self):  # pylint: disable=invalid-name
        """Return id from Link intance.

        Returns:
            string: link id.

        """
        dpid_a = self.endpoint_a.switch.dpid
        port_a = self.endpoint_a.port_number
        dpid_b = self.endpoint_b.switch.dpid
        port_b = self.endpoint_b.port_number
        if dpid_a < dpid_b:
            elements = (dpid_a, port_a, dpid_b, port_b)
        elif dpid_a > dpid_b:
            elements = (dpid_b, port_b, dpid_a, port_a)
        elif port_a < port_b:
            elements = (dpid_a, port_a, dpid_b, port_b)
        else:
            elements = (dpid_b, port_b, dpid_a, port_a)

        str_id = "%s:%s:%s:%s" % elements
        return hashlib.sha256(str_id.encode('utf-8')).hexdigest()

    @property
    def available_tags(self):
        """Return the available tags for the link.

        Based on the endpoint tags.
        """
        return [tag for tag in self.endpoint_a.available_tags if tag in
                self.endpoint_b.available_tags]

    def use_tag(self, tag):
        """Remove a specific tag from available_tags if it is there.

        Deprecated: use only the get_next_available_tag method.
        """
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
        # Copy the available tags because in case of error
        # we will remove and add elements to the available_tags
        available_tags_a = self.endpoint_a.available_tags.copy()
        available_tags_b = self.endpoint_b.available_tags.copy()

        for tag in available_tags_a:
            # Tag does not exist in endpoint B. Try another tag.
            if tag not in available_tags_b:
                continue

            # Tag already in use. Try another tag.
            if not self.endpoint_a.use_tag(tag):
                continue

            # Tag already in use in B. Mark the tag as available again.
            if not self.endpoint_b.use_tag(tag):
                self.endpoint_a.make_tag_available(tag)
                continue

            # Tag used successfully by both endpoints. Returning.
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
