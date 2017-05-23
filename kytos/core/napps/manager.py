"""Manage Network Application files."""
import json
import logging
import shutil
import urllib
from pathlib import Path

from kytos.core.napps import NApp

log = logging.getLogger(__name__)


class NAppsManager:
    """Deal with NApps at filesystem level and ask Kytos to (un)load NApps."""

    def __init__(self, controller):
        """Need the controller for configuration paths and (un)loading NApps.

        Args:
            controller (kytos.Controller): Controller to (un)load NApps.
        """
        self._config = controller.options

        self._controller = controller

        self._enabled = Path(self._config.napps)
        self._installed = self._enabled / '.installed'

    def enable(self, napp_uri):
        """Enable a NApp if not already enabled.

        Raises:
            FileNotFoundError: If NApp is not installed.
            PermissionError: No filesystem permission to enable NApp.
        """
        napp = NApp.create_from_uri(napp_uri)
        enabled = self._enabled / napp.username / napp.name
        installed = self._installed / napp.username / napp.name

        if not installed.is_dir():
            log.error("Failed to enable NApp %s. NApp not installed.",
                      napp.id)
        elif not enabled.exists():
            self._create_module(enabled.parent)
            try:
                # Create symlink
                enabled.symlink_to(installed)
                if self._controller is not None:
                    self._controller.load_napp(napp.username, napp.name)
                log.info("NApp enabled: %s", napp.id)
            except FileExistsError:
                pass  # OK, NApp was already enabled
            except PermissionError:
                log.error("Failed to enable NApp %s. Permission denied.",
                          napp.id)

    def enable_all(self):
        """Enable all napps already installed and disabled."""
        for napp in self.list_disabled():
            self.enable(napp.id)

    def disable(self, napp_uri):
        """Disable a NApp if it is enabled."""
        napp = NApp.create_from_uri(napp_uri)
        enabled = self._enabled / napp.username / napp.name
        try:
            enabled.unlink()
            log.info("NApp disabled: %s", napp.id)
            if self._controller is not None:
                self._controller.unload_napp(napp.username, napp.name)
        except FileNotFoundError:
            pass  # OK, it was already disabled

    def disable_all(self):
        """Disable all napps already installed and enabled."""
        for napp in self.list_enabled():
            self.disable(napp.id)

    def install(self, napp_uri, enable=True):
        """Install and enable a NApp from his repository.

        By default, install procedure will also enable the NApp. If you only
        want to install and keep NApp disabled, please use enable=False.
        """
        napp = NApp.create_from_uri(napp_uri)

        if napp in self.list():
            log.warning("Unable to install NApp %s. Already installed.", napp)
            return False

        if not napp.repository:
            napp.repository = self._controller.options.napps_repositories[0]

        pkg_folder = None
        try:
            pkg_folder = napp.download()
            napp_folder = self._get_local_folder(napp, pkg_folder)
            dst = self._installed / napp.username / napp.name
            self._create_module(dst.parent)
            shutil.move(str(napp_folder), str(dst))
        finally:
            if pkg_folder and pkg_folder.exists():
                shutil.rmtree(str(pkg_folder))

        log.info("New NApp installed: %s", napp)

        napp = NApp.create_from_json(dst/'kytos.json')
        for napp_dependency_uri in napp.napp_dependencies:
            self.install(napp_dependency_uri, enable)

        if enable:
            return self.enable(napp_uri)

        return True

    def uninstall(self, napp_uri):
        """Remove a NApp from filesystem, if existent."""
        napp = NApp.create_from_uri(napp_uri)

        if self.is_enabled(napp_uri):
            log.warning("Unable to uninstall NApp %s. NApp currently in use.",
                        napp)
            return False

        if self.is_installed(napp_uri):
            installed = self._installed / napp.username / napp.name
            if installed.is_symlink():
                installed.unlink()
            else:
                shutil.rmtree(str(installed))
            log.info("NApp uninstalled: %s", napp)
        else:
            log.warning("Unable to uninstall NApp %s. Already uninstalled.",
                        napp)
        return True

    def is_enabled(self, napp_uri):
        """Whether a NApp is enabled or not on this controller."""
        napp = NApp.create_from_uri(napp_uri)
        return napp in self.list_enabled()

    def is_installed(self, napp_uri):
        """Whether a NApp is installed or not on this controller."""
        napp = NApp.create_from_uri(napp_uri)
        return napp in self.list()

    def list(self):
        """List all NApps on this controller."""
        disabled = self.list_disabled()
        enabled = self.list_enabled()
        return enabled + disabled

    def list_enabled(self):
        """List all enabled NApps on this controller."""
        enabled = self._list_all(self._enabled)
        for napp in enabled:
            napp.enabled = True
        return enabled

    def list_disabled(self):
        """List all disabled NApps on this controller."""
        installed = set(self._list_all(self._installed))
        enabled = set(self.list_enabled())
        return list(installed - enabled)

    def search(self, pattern, use_cache=False):
        """Search for NApps in NApp repositories matching a pattern."""
        # ISSUE #347, we need to loop here over all repositories
        repo = eval(self._config.napps_repositories)[0]  # noqa

        if use_cache:
            # ISSUE #346, we should use cache here
            pass

        result = urllib.request.urlretrieve("{}/.database".format(repo))[0]
        with open(result, 'r') as fp:
            napps_json = json.load(fp)

        napps = [NApp.create_from_dict(napp_json) for napp_json in napps_json]
        return [napp for napp in napps if napp.match(pattern)]

    @staticmethod
    def _list_all(napps_dir):
        """List all NApps found in ``napps_dir``."""
        if not napps_dir.exists():
            log.warning("NApps dir (%s) doesn't exist.", napps_dir)
            return []

        jsons = napps_dir.glob('*/*/kytos.json')
        return [NApp.create_from_json(j) for j in jsons]

    @staticmethod
    def _create_module(folder):
        """Create module folder with empty __init__.py if it doesn't exist.

        Args:
            folder (pathlib.Path): Module path.
        """
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True, mode=0o755)
            (folder / '__init__.py').touch()

    @staticmethod
    def _get_local_folder(napp, root=None):
        """Return local NApp root folder.

        Search for kytos.json in _./_ folder and _./user/napp_.

        Args:
            root (pathlib.Path): Where to begin searching.

        Raises:
            FileNotFoundError: If there is no such local NApp.

        Return:
            pathlib.Path: NApp root folder.
        """
        if root is None:
            root = Path()
        for folders in ['.'], [napp.username, napp.name]:
            kytos_json = root / Path(*folders) / 'kytos.json'
            if kytos_json.exists():
                with kytos_json.open() as f:
                    meta = json.load(f)
                    if meta['username'] == napp.username and \
                            meta['name'] == napp.name:
                        return kytos_json.parent
        raise FileNotFoundError('kytos.json not found.')
