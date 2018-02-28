"""Module with common classes for the controller."""

__all__ = ('GenericEntity',)


class GenericEntity:
    """Generic Class that represents any Entity."""

    def __init__(self):
        """Create the GenericEntity object with empty metadata dictionary."""
        self.metadata = {}

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

    def update_metadata(self, key, value):
        """Overwrite a specific metadata."""
        self.metadata[key] = value

    def clear_metadata(self):
        """Remove all metadata information."""
        self.metadata = {}

    def extend_metadata(self, metadatas, force=False):
        """Extend the metadata information.

        If force is True any existing value is overwritten.
        """
        if force:
            return self.metadata.update(metadatas)

        for key, value in metadatas.items():
            self.add_metadata(key, value)
