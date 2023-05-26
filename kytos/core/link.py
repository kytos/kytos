"""Module with all classes related to links.

Links are low level abstractions representing connections between two
interfaces.
"""
import json
from collections import OrderedDict
from threading import Lock

from kytos.core.common import EntityStatus, GenericEntity
from kytos.core.exceptions import (KytosLinkCreationError,
                                   KytosNoTagAvailableError)
from kytos.core.id import LinkID
from kytos.core.interface import TAGType


class Link(GenericEntity):
    """Define a link between two Endpoints."""

    status_funcs = OrderedDict()
    _get_available_vlans_lock = Lock()

    def __init__(self, endpoint_a, endpoint_b):
        """Create a Link instance and set its attributes.

        Two kytos.core.interface.Interface are required as parameters.
        """
        if endpoint_a is None:
            raise KytosLinkCreationError("endpoint_a cannot be None")
        if endpoint_b is None:
            raise KytosLinkCreationError("endpoint_b cannot be None")
        self.endpoint_a = endpoint_a
        self.endpoint_b = endpoint_b
        self._id = LinkID(endpoint_a.id, endpoint_b.id)
        super().__init__()

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Link({self.endpoint_a!r}, {self.endpoint_b!r}, {self.id})"

    @classmethod
    def register_status_func(cls, name: str, func):
        """Register status func given its name and a callable at setup time."""
        cls.status_funcs[name] = func

    @property
    def status(self):
        """Return the current status of the Entity."""
        state = super().status
        if state == EntityStatus.DISABLED:
            return state

        for status_func in self.status_funcs.values():
            if status_func(self) == EntityStatus.DOWN:
                return EntityStatus.DOWN
        return state

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
        return self._id

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
        with self._get_available_vlans_lock:
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

            raise KytosNoTagAvailableError(self)

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
        vlans_b = self._get_available_vlans(self.endpoint_b)
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
                'enabled': self.is_enabled(),
                'status': self.status.value}

    def as_json(self):
        """Return the Link as a JSON string."""
        return json.dumps(self.as_dict())

    @classmethod
    def from_dict(cls, link_dict):
        """Return a Link instance from python dictionary."""
        return cls(link_dict.get('endpoint_a'),
                   link_dict.get('endpoint_b'))
