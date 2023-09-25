"""Module with all classes related to links.

Links are low level abstractions representing connections between two
interfaces.
"""
import json
import operator
from collections import OrderedDict, defaultdict
from functools import reduce
from threading import Lock
from typing import Union

from kytos.core.common import EntityStatus, GenericEntity
from kytos.core.exceptions import (KytosLinkCreationError,
                                   KytosNoTagAvailableError)
from kytos.core.id import LinkID
from kytos.core.interface import Interface, TAGType


class Link(GenericEntity):
    """Define a link between two Endpoints."""

    status_funcs = OrderedDict()
    status_reason_funcs = OrderedDict()
    _get_available_vlans_lock = defaultdict(Lock)

    def __init__(self, endpoint_a, endpoint_b):
        """Create a Link instance and set its attributes.

        Two kytos.core.interface.Interface are required as parameters.
        """
        if endpoint_a is None:
            raise KytosLinkCreationError("endpoint_a cannot be None")
        if endpoint_b is None:
            raise KytosLinkCreationError("endpoint_b cannot be None")
        self._id = LinkID(endpoint_a.id, endpoint_b.id)
        if self._id.interfaces[0] == endpoint_b.id:
            self.endpoint_a: Interface = endpoint_b
            self.endpoint_b: Interface = endpoint_a
        else:
            self.endpoint_a: Interface = endpoint_a
            self.endpoint_b: Interface = endpoint_b

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

    @classmethod
    def register_status_reason_func(cls, name: str, func):
        """Register status reason func given its name
        and a callable at setup time."""
        cls.status_reason_funcs[name] = func

    @property
    def status_reason(self):
        """Return the reason behind the current status of the entity."""
        return reduce(
            operator.or_,
            map(
                lambda x: x(self),
                self.status_reason_funcs.values()
            ),
            super().status_reason
        )

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

    def available_tags(self, tag_type: str = 'vlan') -> list[list[int]]:
        """Return the available tags for the link.

        Based on the endpoint tags.
        """
        tag_iterator = Interface.range_intersection(
            self.endpoint_a.available_tags[tag_type],
            self.endpoint_b.available_tags[tag_type],
        )
        available_tags = list(tag_iterator)
        return available_tags

    def is_tag_available(self, tag: int, tag_type: str = 'vlan'):
        """Check if a tag is available."""
        return (self.endpoint_a.is_tag_available(tag, tag_type) and
                self.endpoint_b.is_tag_available(tag, tag_type))

    def get_next_available_tag(
        self,
        controller,
        link_id,
        tag_type: str = 'vlan'
    ) -> int:
        """Return the next available tag if exists."""
        with self._get_available_vlans_lock[link_id]:
            with self.endpoint_a._tag_lock:
                with self.endpoint_b._tag_lock:
                    ava_tags_a = self.endpoint_a.available_tags[tag_type]
                    ava_tags_b = self.endpoint_b.available_tags[tag_type]
                    tags = Interface.range_intersection(ava_tags_a,
                                                        ava_tags_b)
                    try:
                        tag, _ = next(tags)
                        self.endpoint_a.use_tags(
                            controller, tag, use_lock=False
                        )
                        self.endpoint_b.use_tags(
                            controller, tag, use_lock=False
                        )
                        return tag
                    except StopIteration:
                        raise KytosNoTagAvailableError(self)

    def make_tags_available(
        self,
        controller,
        tags: Union[int, list[int]],
        link_id,
        tag_type: str = 'vlan'
    ) -> tuple[bool, bool]:
        """Add a specific tag in available_tags."""
        with self._get_available_vlans_lock[link_id]:
            with self.endpoint_a._tag_lock:
                with self.endpoint_b._tag_lock:
                    result_a = self.endpoint_a.make_tags_available(
                        controller, tags, tag_type, False
                    )
                    result_b = self.endpoint_b.make_tags_available(
                        controller, tags, tag_type, False
                    )
        return result_a, result_b

    def available_vlans(self):
        """Get all available vlans from each interface in the link."""
        vlans_a = self._get_available_vlans(self.endpoint_a)
        vlans_b = self._get_available_vlans(self.endpoint_b)
        return [vlan for vlan in vlans_a if vlan in vlans_b]

    @staticmethod
    def _get_available_vlans(endpoint):
        """Return all vlans from endpoint."""
        vlans = endpoint.available_tags
        return [vlan for vlan in vlans if vlan == TAGType.VLAN.value]

    def as_dict(self):
        """Return the Link as a dictionary."""
        return {
            'id': self.id,
            'endpoint_a': self.endpoint_a.as_dict(),
            'endpoint_b': self.endpoint_b.as_dict(),
            'metadata': self.get_metadata_as_dict(),
            'active': self.is_active(),
            'enabled': self.is_enabled(),
            'status': self.status.value,
            'status_reason': sorted(self.status_reason),
        }

    def as_json(self):
        """Return the Link as a JSON string."""
        return json.dumps(self.as_dict())

    @classmethod
    def from_dict(cls, link_dict):
        """Return a Link instance from python dictionary."""
        return cls(link_dict.get('endpoint_a'),
                   link_dict.get('endpoint_b'))
