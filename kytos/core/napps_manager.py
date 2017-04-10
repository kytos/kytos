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
        """List of (username, napp_name) found in enabled napps folder."""
        folder = self._enabled
        napps = []
        ignored_paths = set(['.installed', '__pycache__', '__init__.py'])
        for username in set(listdir(folder)) - ignored_paths:
            username_dir = path.join(folder, username)
            for napp_name in set(listdir(username_dir)) - ignored_paths:
                napps.append((username, napp_name))
        return sorted(napps)
