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
    """Generic Class that represents any Entity."""

    def __init__(self):
        """Create the GenericEntity object with empty metadata dictionary."""
        options = KytosConfig().options['daemon']
        self.metadata = {}
        # operational status with True or False
        self.__active = True
        # administrative status with True or False
        self.__enabled = options.enable_entities_by_default

    @property
    def enabled(self):
        """Getter method to active attribute.

        Returns:
            boolean: Enabled status can be True or False.

        """
        return self.__enabled

    @enabled.setter
    def enabled(self, boolean_value):
        """Setter method to active attribute.

        Args:
            boolean_value: Boolean value to be setted in the enabled attribute.

        """
        self.__enabled = boolean_value

    @property
    def active(self):
        """Getter method to active attribute.

        Returns:
            boolean: Active status can be True or False.

        """
        return self.__active

    @active.setter
    def active(self, boolean_value):
        """Setter method to active attribute.

        Args:
            boolean_value: Boolean value to be setted in the active attribute.

        """
        self.__active = boolean_value

    @property
    def status(self):
        """Return the current status of the Entity."""
        if self.enabled and self.active:
            return EntityStatus.UP
        elif self.is_administrative_down():
            return EntityStatus.DISABLED
        return EntityStatus.DOWN

    def is_administrative_down(self):
        """Return True for disabled Entities."""
        return not self.enabled

    def enable(self):
        """Administratively enable the Entity.

        Although this method only sets an 'enabled' flag, always prefer to use
        it instead of setting it manually. This allows us to change the
        behavior on the future.
        """
        self.enabled = True

    def disable(self):
        """Administratively disable the Entity.

        This method can disable other related entities. For this behavior,
        rewrite it on the child classes.
        """
        self.enabled = False

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
            return self.metadata.update(metadatas)

        for key, value in metadatas.items():
            self.add_metadata(key, value)
