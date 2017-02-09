"""Manage Network Application files."""
from os import listdir, path


class NAppsManager:
    """Deal with NApps at filesystem level."""

    def __init__(self, enabled_napps_path):
        """Use folder locations from ``options``.

        Args:
            enabled_napps_path (str): Folder of the enabled napps.
        """
        self._enabled = enabled_napps_path

    def get_enabled(self):
        """List of (author, napp_name) found in enabled napps folder."""
        folder = self._enabled
        napps = []
        ignored_paths = set(['.installed', '__pycache__', '__init__.py'])
        for author in set(listdir(folder)) - ignored_paths:
            author_dir = path.join(folder, author)
            for napp_name in set(listdir(author_dir)) - ignored_paths:
                napps.append((author, napp_name))
        return sorted(napps)
