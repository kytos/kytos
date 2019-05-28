"""Manage Network Application files."""
import json
import logging
import re
import shutil
from pathlib import Path

from kytos.core.napps import NApp

LOG = logging.getLogger(__name__)


class NAppsManager:
    """Deal with NApps at filesystem level and ask Kytos to (un)load NApps."""

    def __init__(self, controller=None, base_path=None):
        """Need the controller for configuration paths and (un)loading NApps.

        Args:
            controller (kytos.Controller): Controller to (un)load NApps.
            base_path (pathlib.Path): base path for enabled NApps.
                This will be supported while kytos-utils still imports
                kytos.core directly, and may be removed when it calls Kytos'
                Web API.
        """
        self._controller = controller

        if base_path:
            self._enabled_path = base_path
        else:
            self._config = controller.options
            self._enabled_path = Path(self._config.napps)

        self._installed_path = self._enabled_path / '.installed'

    def install(self, napp_uri, enable=True):
        """Install and enable a NApp from its repository.

        By default, install procedure will also enable the NApp. If you only
        want to install and keep NApp disabled, please use enable=False.
        """
        napp = NApp.create_from_uri(napp_uri)

        if napp in self.get_all_napps():
            LOG.warning("Unable to install NApp %s. Already installed.", napp)
            return False

        if not napp.repository:
            napp.repository = self._controller.options.napps_repositories[0]

        pkg_folder = None
        try:
            pkg_folder = napp.download()
            napp_folder = self._find_napp(napp, pkg_folder)
            dst = self._installed_path / napp.username / napp.name
            self._create_module(dst.parent)
            shutil.move(str(napp_folder), str(dst))
        finally:
            if pkg_folder and pkg_folder.exists():
                shutil.rmtree(str(pkg_folder))

        LOG.info("New NApp installed: %s", napp)

        napp = NApp.create_from_json(dst/'kytos.json')
        for uri in napp.napp_dependencies:
            self.install(uri, enable)

        if enable:
            return self.enable(napp.username, napp.name)

        return True

    def uninstall(self, username, napp_name):
        """Remove a NApp from filesystem, if existent."""
        napp_id = "{}/{}".format(username, napp_name)

        if self.is_enabled(username, napp_name):
            LOG.warning("Unable to uninstall NApp %s. NApp currently in use.",
                        napp_id)
            return False

        new_manager = NewNAppManager(self._installed_path)
        napp = new_manager.napps[napp_id]
        deps = napp.napp_dependencies

        if deps and napp.meta:
            LOG.info('Uninstalling Meta-NApp %s dependencies: %s', napp, deps)
            for uri in deps:
                username, napp_name = self.get_napp_fullname_from_uri(uri)
                self.uninstall(username, napp_name)

        if self.is_installed(username, napp_name):
            installed = self._installed_path / napp_id
            if installed.is_symlink():
                installed.unlink()
            else:
                shutil.rmtree(str(installed))
            LOG.info("NApp uninstalled: %s", napp_id)
        else:
            LOG.warning("Unable to uninstall NApp %s. Already uninstalled.",
                        napp_id)
        return True

    def enable(self, username, napp_name):
        """Enable a NApp if not already enabled."""
        napp_id = "{}/{}".format(username, napp_name)

        enabled = self._enabled_path / napp_id
        installed = self._installed_path / napp_id

        new_manager = NewNAppManager(self._installed_path)
        napp = new_manager.napps[napp_id]
        deps = napp.napp_dependencies

        if deps and napp.meta:
            LOG.info('Enabling Meta-NApp %s dependencies: %s', napp, deps)
            for uri in deps:
                username, napp_name = self.get_napp_fullname_from_uri(uri)
                self.enable(username, napp_name)

        if not installed.is_dir():
            LOG.error("Failed to enable NApp %s. NApp not installed.", napp_id)
        elif not enabled.exists():
            self._create_module(enabled.parent)
            try:
                # Create symlink
                enabled.symlink_to(installed)
                if self._controller is not None:
                    self._controller.load_napp(username, napp_name)
                LOG.info("NApp enabled: %s", napp_id)
            except FileExistsError:
                pass  # OK, NApp was already enabled
            except PermissionError:
                LOG.error("Failed to enable NApp %s. Permission denied.",
                          napp_id)

        return True

    def disable(self, username, napp_name):
        """Disable a NApp if it is enabled."""
        napp_id = "{}/{}".format(username, napp_name)
        enabled = self._enabled_path / napp_id

        new_manager = NewNAppManager(self._installed_path)
        napp = new_manager.napps[napp_id]
        deps = napp.napp_dependencies

        if deps and napp.meta:
            LOG.info('Disabling Meta-NApp %s dependencies: %s', napp, deps)
            for uri in deps:
                username, napp_name = self.get_napp_fullname_from_uri(uri)
                self.disable(username, napp_name)

        try:
            enabled.unlink()
            LOG.info("NApp disabled: %s", napp_id)
            if self._controller is not None:
                self._controller.unload_napp(username, napp_name)
        except FileNotFoundError:
            pass  # OK, it was already disabled

        return True

    def enable_all(self):
        """Enable all napps already installed and disabled."""
        for napp in self.get_disabled_napps():
            self.enable(napp.username, napp.name)

    def disable_all(self):
        """Disable all napps already installed and enabled."""
        for napp in self.get_enabled_napps():
            self.disable(napp.username, napp.name)

    def is_enabled(self, username, napp_name):
        """Whether a NApp is enabled or not on this controller FS."""
        napp_id = "{}/{}".format(username, napp_name)

        napp = NApp.create_from_uri(napp_id)
        return napp in self.get_enabled_napps()

    def is_installed(self, username, napp_name):
        """Whether a NApp is installed or not on this controller."""
        napp_id = "{}/{}".format(username, napp_name)
        napp = NApp.create_from_uri(napp_id)
        return napp in self.get_all_napps()

    @staticmethod
    def get_napp_fullname_from_uri(uri):
        """Parse URI and get (username, napp_name) tuple."""
        regex = r'^(((https?://|file://)(.+))/)?(.+?)/(.+?)/?(:(.+))?$'
        match = re.match(regex, uri)
        username = match.groups()[4]
        napp_name = match.groups()[5]
        return username, napp_name

    def get_all_napps(self):
        """List all NApps on this controller FS."""
        return self.get_installed_napps()

    def get_enabled_napps(self):
        """Return all enabled NApps on this controller FS."""
        enabled = self.get_napps_from_path(self._enabled_path)
        for napp in enabled:
            # We should also check if the NApp is enabled on controller
            napp.enabled = True
        return enabled

    def get_disabled_napps(self):
        """Return all disabled NApps on this controller FS."""
        installed = set(self.get_installed_napps())
        enabled = set(self.get_enabled_napps())
        return list(installed - enabled)

    def get_installed_napps(self):
        """Return all NApps installed on this controller FS."""
        return self.get_napps_from_path(self._installed_path)

    def get_napp_metadata(self, username, napp_name, key):
        """Return a value from kytos.json.

        Args:
            username (string): A Username.
            napp_name (string): A NApp name
            key (string): Key used to get the value within kytos.json.

        Returns:
            meta (object): Value stored in kytos.json.

        """
        napp_id = "{}/{}".format(username, napp_name)
        kytos_json = self._installed_path / napp_id / 'kytos.json'
        try:
            with kytos_json.open() as file_descriptor:
                meta = json.load(file_descriptor)
                return meta[key]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            LOG.warning("NApp metadata load failed: %s/kytos.json", napp_id)
            return ''

    @staticmethod
    def get_napps_from_path(path: Path):
        """List all NApps found in ``napps_dir``."""
        if not path.exists():
            LOG.warning("NApps dir (%s) doesn't exist.", path)
            return []

        jsons = path.glob('*/*/kytos.json')
        return [NApp.create_from_json(j) for j in jsons]

    @staticmethod
    def _create_module(path: Path):
        """Create module with empty __init__.py in `path` if it doesn't exist.

        Args:
            path: Module path.
        """
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True, mode=0o755)
        (path / '__init__.py').touch()

    @staticmethod
    def _find_napp(napp, root: Path = None) -> Path:
        """Return local NApp root folder.

        Search for kytos.json in _./_ folder and _./user/napp_.

        Args:
            root: Where to begin searching.

        Raises:
            FileNotFoundError: If there is no such local NApp.

        Returns:
            NApp root folder.

        """
        if root is None:
            root = Path()
        for folders in ['.'], [napp.username, napp.name]:
            kytos_json = root / Path(*folders) / 'kytos.json'
            if kytos_json.exists():
                with kytos_json.open() as file_descriptor:
                    meta = json.load(file_descriptor)
                    if meta['username'] == napp.username and \
                            meta['name'] == napp.name:
                        return kytos_json.parent
        raise FileNotFoundError('kytos.json not found.')


class NewNAppManager:
    """A more simple NApp Manager, for just one NApp at a time."""

    def __init__(self, base_path: Path):
        """Create a manager from a NApp base path."""
        self.base_path = base_path
        self.napps = {napp.id: napp for napp in self._find_napps()}

    def _find_napps(self):
        return NAppsManager.get_napps_from_path(self.base_path)
