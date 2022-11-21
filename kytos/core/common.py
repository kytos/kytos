"""Module with common classes for the controller."""
from enum import Enum

from kytos.core.config import KytosConfig

__all__ = ('GenericEntity',)


class EntityStatus(Enum):
    """Enumeration of possible statuses for GenericEntity instances."""

    UP = 1  # pylint: disable=invalid-name
    DISABLED = 2
    DOWN = 3


class GenericEntity:
    """Generic class that represents any Entity."""

    def __init__(self):
        """Create the GenericEntity object with empty metadata dictionary."""
        options = KytosConfig().options['daemon']
        self.metadata = {}

        self._active: bool = True
        self._enabled: bool = options.enable_entities_by_default

    def is_enabled(self) -> bool:
        """Return the *administrative* status of the entity."""
        return self._enabled

    def is_active(self) -> bool:
        """Return the *operational* status of the entity."""
        return self._active

    def activate(self):
        """Activate the entity."""
        self._active = True

    def deactivate(self):
        """Deactivate the entity."""
        self._active = False

    @property
    def status(self):
        """Return the current status of the Entity."""
        if self.is_enabled() and self.is_active():
            return EntityStatus.UP
        if self.is_administrative_down():
            return EntityStatus.DISABLED
        return EntityStatus.DOWN

    def is_administrative_down(self):
        """Return True for disabled Entities."""
        return not self.is_enabled()

    def enable(self):
        """Administratively enable the Entity.

        Although this method only sets an 'enabled' flag, always prefer to use
        it instead of setting it manually. This allows us to change the
        behavior in the future.
        """
        self._enabled = True

    def disable(self):
        """Administratively disable the Entity.

        This method can disable other related entities. For this behavior,
        rewrite it on the child classes.
        """
        self._enabled = False

    def add_metadata(self, key, value):
        """Add a new metadata (key, value)."""
        if key in self.metadata:
            return False

        self.metadata[key] = value
        return True

    def remove_metadata(self, key):
        """Try to remove a specific metadata."""
        try:
            del self.metadata[key]
            return True
        except KeyError:
            return False

    def get_metadata(self, key):
        """Try to get a specific metadata."""
        return self.metadata.get(key)

    def get_metadata_as_dict(self):
        """Get all metadata values as dict."""
        metadata = dict(self.metadata)
        for key, value in self.metadata.items():
            if hasattr(value, 'as_dict'):
                metadata[key] = value.as_dict()
        return metadata

    def update_metadata(self, key, value):
        """Overwrite a specific metadata."""
        self.metadata[key] = value

    def clear_metadata(self):
        """Remove all metadata information."""
        self.metadata = {}

    def extend_metadata(self, metadatas, force=True):
        """Extend the metadata information.

        If force is True any existing value is overwritten.
        """
        if force:
            self.metadata.update(metadatas)
            return

        for key, value in metadatas.items():
            self.add_metadata(key, value)
