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
