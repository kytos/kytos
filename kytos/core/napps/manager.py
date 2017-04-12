"""Manage Network Application files."""
import json
import logging
import os
import re
import shutil
import sys
import tarfile
import tempfile
import urllib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from kytos.utils.client import NAppsClient

log = logging.getLogger(__name__)

class NApp:
    def __init__(self, username=None, name=None, version=None,
                 repository=None):
        self.username = username
        self.name = name
        self.version = version
        self.repository = repository
        self.enabled = False

    def __str__(self):
        return "{}/{}".format(self.username, self.name)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.id == other.id)

    @property
    def id(self):
        return str(self)

    @property
    def uri(self):
        version = self.version if self.version else 'latest'
        if self._has_valid_repository():
            return "{}/{}-{}".format(self.repository, self.id, version)
            # Use the next line after Diraol fix redirect using ":" for version
            #return "{}/{}:{}".format(self.repository, self.id, version)

    @property
    def package_url(self):
        if self.uri:
            return "{}.napp".format(self.uri)

    @staticmethod
    def create_from_json(filename):
        """Method used to update object attributes based on kytos.json."""
        napp = NApp()
        with open(filename, encoding='utf-8') as data_file:
            data = json.loads(data_file.read())

        for attribute, value in data.items():
            print(attribute, value)
            setattr(napp, attribute, value)

        return napp

    @staticmethod
    def create_from_uri(uri):
        regex =  r'^(((https?://|file://)(.+))/)?(.+?)/(.+?)/?(:(.+))?$'
        match = re.match(regex, uri)

        if match:
            return NApp(username=match.groups()[4],
                        name=match.groups()[5],
                        version=match.groups()[7],
                        repository=match.groups()[1])

    def download(self):
        """Download NApp package from his repository.

        Raises:
            urllib.error.HTTPError: If download is not successful.

        Return:
            str: Downloaded temp filename.
        """
        if self.package_url:
            package_filename = urllib.request.urlretrieve(self.package_url)[0]
            extracted = self._extract(package_filename)
            Path(package_filename).unlink()
            self._update_repo_file(extracted)
            return extracted

    def as_json(self):
        """Dump all NApp attributes on a json format."""
        pass

    @staticmethod
    def _extract(filename):
        """Extract package to a temporary folder.

        Return:
            pathlib.Path: Temp dir with package contents.
        """
        tmp = tempfile.mkdtemp(prefix='kytos-napp-')
        with tarfile.open(filename, 'r:xz') as tar:
            tar.extractall(tmp)
        return Path(tmp)

    def _has_valid_repository(self):
        return all([self.username, self.name, self.repository])

    def _update_repo_file(self, destination=None):
        with open("{}/.repo".format(destination), 'w') as fp:
            fp.write(self.repository + '\n')



#napp.download()

# NAPP URI:


# NAPP Identifier:
# [protocol://][repository]

# beraldo/foo:20170909

    # https://napps.kytos.io/repo/beraldo/foo:latest





# controller.napps.install('foo/bar')
#  -> config.repos

#  napp = NApp(username='foo', name='bar', repository='https://napps.kytos.io/repo')
#  napp.install('/var/lib/kytos/napps/.installed', enable=True)


# controller.napps.install('https://napps.kytos.io/repo/foo/bar')
# controller.napps.install('https://napps.kytos.io/repo/foo/bar:20170909')
## controller.napps.install('file:///home/beraldo/napps/foo/bar')


class NAppsManager:
    """Deal with NApps at filesystem level and ask Kytos to (un)load NApps."""

    def __init__(self, controller):
        """If controller is not informed, the necessary paths must be.

        If ``controller`` is available, NApps will be (un)loaded at runtime and
        you don't need to inform the paths. Otherwise, you should inform the
        required paths for the methods called.

        Args:
            controller (kytos.Controller): Controller to (un)load NApps.
            install_path (str): Folder where NApps should be installed. If
                None, use the controller's configuration.
            enabled_path (str): Folder where enabled NApps are stored. If None,
                use the controller's configuration.
        """
        self._config = controller.options

        self._controller = controller

        self._enabled = Path(self._config.napps)
        self._installed = self._enabled / '.installed'
#
#        self.user = None
#        self.napp = None

    def install(self, napp_uri, enable=True):
        napp = NApp.create_from_uri(napp_uri)

        if napp in self.get_installed2():
            log.warning("Unable to install NApp {}. Already "
                        "installed".format(napp.id))
            return False

        if not napp.repository:
            # Check here what is configured repo
            pass

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

        log.info("New NApp installed: {}".format(napp.id))

        if enable:
            return self.enable(napp_uri)

        return True

    def list(self):
        napps = self.get_installed2()
        enabled = self.get_enabled2()
        for napp in napps:
            if napp in enabled:
                napp.enabled = True
        return napps

#    def set_napp(self, user, napp):
#        """Set info about NApp.
#
#        Args:
#            user (str): NApps Server username.
#            napp (str): NApp name.
#        """
#        self.user = user
#        self.napp = napp
#
#    @property
#    def napp_id(self):
#        """Identifier of NApp."""
#        return '/'.join((self.user, self.napp))
#
    @staticmethod
    def _get_napps2(napps_dir):
        """List of (author, napp_name) found in ``napps_dir``."""
        jsons = napps_dir.glob('*/*/kytos.json')
        return [NApp.create_from_json(j) for j in jsons]

    @staticmethod
    def _get_napps(napps_dir):
        """List of (author, napp_name) found in ``napps_dir``."""
        jsons = napps_dir.glob('*/*/kytos.json')
        return sorted(j.parts[-3:-1] for j in jsons)

    def get_enabled(self):
        """Sorted list of (author, napp_name) of enabled napps."""
        return self._get_napps(self._enabled)

    def get_enabled2(self):
        """Sorted list of (author, napp_name) of enabled napps."""
        return self._get_napps2(self._enabled)

    def get_installed(self):
        """Sorted list of (author, napp_name) of installed napps."""
        return self._get_napps(self._installed)

    def get_installed2(self):
        """Sorted list of (author, napp_name) of installed napps."""
        return self._get_napps2(self._installed)

#    def disable2(self, napp):
#        """Disable a NApp if it is enabled."""
#        path = self._enabled / napp.username / napp.name
#        try:
#            path.unlink()
#            napp.enabled = False
#        except FileNotFoundError:
#            pass  # OK, it was already disabled

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

#    def enable2(self, napp):
#        """Enable a NApp if not already enabled.
#
#        Raises:
#            FileNotFoundError: If NApp is not installed.
#            PermissionError: No filesystem permission to enable NApp.
#        """
#        enabled = self._enabled / napp.username / napp.name
#        installed = self._installed / napp.username / napp.name
#
#        if not installed.is_dir():
#            raise FileNotFoundError('Install NApp {} first.'.format(napp))
#        elif not enabled.exists():
#            self._create_module(enabled.parent)
#            try:
#                # Create symlink
#                enabled.symlink_to(installed)
#            except FileExistsError:
#                pass  # OK, NApp was already enabled
#            except PermissionError:
#                raise PermissionError('Permission error on enabling NApp. Try '
#                                      'with sudo.')

    @staticmethod
    def _create_module(folder):
        """Create module folder with empty __init__.py if it doesn't exist.

        Args:
            folder (pathlib.Path): Module path.
        """
        if not folder.exists():
            folder.mkdir()
            (folder / '__init__.py').touch()

    def is_installed(self):
        """Whether a NApp is installed."""
        return (self.user, self.napp) in self.get_installed()

    def is_installed2(self, napp):
        return napp in self.get_installed2()

#    def get_disabled(self):
#        """Sorted list of (author, napp_name) of disabled napps.
#
#        The difference of installed and enabled.
#        """
#        installed = set(self.get_installed())
#        enabled = set(self.get_enabled())
#        return sorted(installed - enabled)
#
#    def get_description(self, user=None, napp=None):
#        """Return the description from kytos.json."""
#        if user is None:
#            user = self.user
#        if napp is None:
#            napp = self.napp
#        kj = self._installed / user / napp / 'kytos.json'
#        try:
#            with kj.open() as f:
#                meta = json.load(f)
#                return meta['description']
#        except (FileNotFoundError, json.JSONDecodeError, KeyError):
#            return ''
#


#    def is_enabled(self):
#        """Whether a NApp is enabled."""
#        return (self.user, self.napp) in self.get_enabled()

#
    def uninstall(self):
        """Delete code inside NApp directory, if existent."""
        if self.is_installed():
            installed = self._installed / self.user / self.napp
            if installed.is_symlink():
                installed.unlink()
            else:
                shutil.rmtree(str(installed))

    def uninstall2(self, napp):
        """Delete code inside NApp directory, if existent."""
        if self.is_installed2(napp):
            installed = self._installed / napp.username / napp.name
            if installed.is_symlink():
                installed.unlink()
            else:
                shutil.rmtree(str(installed))


#    @staticmethod
#    def valid_name(username):
#        """Check the validity of the given 'name'.
#
#        The following checks are done:
#        - name starts with a letter
#        - name contains only letters, numbers or underscores
#        """
#        return username and re.match(r'[a-zA-Z][a-zA-Z0-9_]{2,}$', username)
#
#    @staticmethod
#    def render_template(templates_path, template_filename, context):
#        """Render Jinja2 template for a NApp structure."""
#        TEMPLATE_ENV = Environment(autoescape=False, trim_blocks=False,
#                                   loader=FileSystemLoader(templates_path))
#        return TEMPLATE_ENV.get_template(template_filename).render(context)
#
#    @staticmethod
#    def search(pattern):
#        """Search all server NApps matching pattern.
#
#        Args:
#            pattern (str): Python regular expression.
#        """
#        def match(napp):
#            """Whether a NApp metadata matches the pattern."""
#            strings = ['{}/{}'.format(napp['author'], napp['name']),
#                       napp['description']] + napp['tags']
#            return any(pattern.match(string) for string in strings)
#
#        napps = NAppsClient().get_napps()
#        return [napp for napp in napps if match(napp)]
#
#    def install_local(self):
#        """Make a symlink in install folder to a local NApp.
#
#        Raises:
#            FileNotFoundError: If NApp is not found.
#        """
#        folder = self._get_local_folder()
#        installed = self._installed / self.user / self.napp
#        self._check_module(installed.parent)
#        installed.symlink_to(folder.resolve())
#
    def _get_local_folder(self, napp, root=None):
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

    def install_remote(self):
        """Download, extract and install NApp."""
        package, pkg_folder = None, None
        try:
            package = self.download()
            pkg_folder = self._extract(package)
            napp_folder = self._get_local_folder(pkg_folder)
            dst = self._installed / self.user / self.napp
            self._check_module(dst.parent)
            shutil.move(str(napp_folder), str(dst))
        finally:
            # Delete temporary files
            if package:
                Path(package).unlink()
            if pkg_folder and pkg_folder.exists():
                shutil.rmtree(str(pkg_folder))

    def install_remote2(self, napp):
        """Download, extract and install NApp."""
        package, pkg_folder = None, None
        try:
            package = self.download(napp)
            pkg_folder = self._extract(package)
            napp_folder = self._get_local_folder(napp, pkg_folder)
            dst = self._installed / napp.username / napp.name
            self._create_module(dst.parent)
            shutil.move(str(napp_folder), str(dst))
        finally:
            # Delete temporary files
            if package:
                Path(package).unlink()
            if pkg_folder and pkg_folder.exists():
                shutil.rmtree(str(pkg_folder))


    def download(self, napp):
        """Download NApp package from server.

        Raises:
            urllib.error.HTTPError: If download is not successful.

        Return:
            str: Downloaded temp filename.
        """
        repo = eval(self._config.napps_repositories)[0]
        uri = os.path.join(repo, napp.username,
                           '{}-latest.napp'.format(napp.name))
        return urllib.request.urlretrieve(uri)[0]

    @staticmethod
    def _extract(filename):
        """Extract package to a temporary folder.

        Return:
            pathlib.Path: Temp dir with package contents.
        """
        tmp = tempfile.mkdtemp(prefix='kytos')
        with tarfile.open(filename, 'r:xz') as tar:
            tar.extractall(tmp)
        return Path(tmp)

#    @classmethod
#    def create_napp(cls):
#        """Bootstrap a basic NApp strucutre for you to develop your NApp.
#
#        This will create, on the current folder, a clean structure of a NAPP,
#        filling some contents on this structure.
#        """
#        base = os.environ.get('VIRTUAL_ENV') or '/'
#
#        templates_path = os.path.join(base, 'etc', 'skel', 'kytos',
#                                      'napp-structure', 'author', 'napp')
#        author = None
#        napp_name = None
#        description = None
#        print('--------------------------------------------------------------')
#        print('Welcome to the bootstrap process of your NApp.')
#        print('--------------------------------------------------------------')
#        print('In order to answer both the author name and the napp name,')
#        print('You must follow this naming rules:')
#        print(' - name starts with a letter')
#        print(' - name contains only letters, numbers or underscores')
#        print(' - at least three characters')
#        print('--------------------------------------------------------------')
#        print('')
#        msg = 'Please, insert your NApps Server username: '
#        while not cls.valid_name(author):
#            author = input(msg)
#
#        while not cls.valid_name(napp_name):
#            napp_name = input('Please, insert your NApp name: ')
#
#        msg = 'Please, insert a brief description for your NApp [optional]: '
#        description = input(msg)
#        if not description:
#            description = \
#                '# TODO: <<<< Insert here your NApp description >>>>'  # noqa
#
#        context = {'author': author, 'napp': napp_name,
#                   'description': description}
#
#        #: Creating the directory structure (author/name)
#        os.makedirs(author, exist_ok=True)
#        #: Creating ``__init__.py`` files
#        with open(os.path.join(author, '__init__.py'), 'w'):
#            pass
#
#        os.makedirs(os.path.join(author, napp_name))
#        with open(os.path.join(author, napp_name, '__init__.py'), 'w'):
#            pass
#
#        #: Creating the other files based on the templates
#        templates = os.listdir(templates_path)
#        templates.remove('__init__.py')
#        for tmp in templates:
#            fname = os.path.join(author, napp_name, tmp.rsplit('.template')[0])
#            with open(fname, 'w') as file:
#                content = cls.render_template(templates_path, tmp, context)
#                file.write(content)
#
#        msg = '\nCongratulations! Your NApp have been bootstrapped!\nNow you '
#        msg += 'can go to the directory {}/{} and begin to code your NApp.'
#        print(msg.format(author, napp_name))
#        print('Have fun!')
#

#    @staticmethod
#    def build_napp_package(napp_name):
#        """Build the .napp file to be sent to the napps server.
#
#        Args:
#            napp_identifier (str): Identifier formatted as <author>/<napp_name>
#
#        Return:
#            file_payload (binary): The binary representation of the napp
#                package that will be POSTed to the napp server.
#        """
#        ignored_extensions = ['.swp', '.pyc', '.napp']
#        ignored_dirs = ['__pycache__']
#        files = os.listdir()
#        for filename in files:
#            if os.path.isfile(filename) and '.' in filename and \
#                    filename.rsplit('.', 1)[1] in ignored_extensions:
#                files.remove(filename)
#            elif os.path.isdir(filename) and filename in ignored_dirs:
#                files.remove(filename)
#
#        # Create the '.napp' package
#        napp_file = tarfile.open(napp_name + '.napp', 'x:xz')
#        for local_f in files:
#            napp_file.add(local_f)
#        napp_file.close()
#
#        # Get the binary payload of the package
#        file_payload = open(napp_name + '.napp', 'rb')
#
#        # remove the created package from the filesystem
#        os.remove(napp_name + '.napp')
#
#        return file_payload
#
#    @staticmethod
#    def create_metadata(*args, **kwargs):
#        """Generate the metadata to send the napp package."""
#        json_filename = kwargs.get('json_filename', 'kytos.json')
#        readme_filename = kwargs.get('readme_filename', 'README.rst')
#        ignore_json = kwargs.get('ignore_json', False)
#        metadata = {}
#
#        if not ignore_json:
#            try:
#                with open(json_filename) as json_file:
#                    metadata = json.load(json_file)
#            except FileNotFoundError:
#                print("ERROR: Could not access kytos.json file.")
#                sys.exit(1)
#
#        try:
#            with open(readme_filename) as readme_file:
#                metadata['readme'] = readme_file.read()
#        except FileNotFoundError:
#            metadata['readme'] = ''
#
#        return metadata
#
#    def upload(self, *args, **kwargs):
#        """Create package and upload it to NApps Server.
#
#        Raises:
#            FileNotFoundError: If kytos.json is not found.
#        """
#        metadata = self.create_metadata(*args, **kwargs)
#        package = self.build_napp_package(metadata['name'])
#
#        NAppsClient().upload_napp(metadata, package)
#
#    def delete(self):
#        """Delete a NApp.
#
#        Raises:
#            requests.HTTPError: When there's a server error.
#        """
#        client = NAppsClient(self._config)
#        client.delete(self.user, self.napp)



#"""Manage Network Application files."""
#from os import listdir, path
#
#
#class NAppsManager:
#    """Deal with NApps at filesystem level."""
#
#    def __init__(self, enabled_napps_path):
#        """Use folder locations from ``options``.
#
#        Args:
#            enabled_napps_path (str): Folder of the enabled napps.
#        """
#        self._enabled = enabled_napps_path
#
#    def get_enabled(self):
#        """List of (username, napp_name) found in enabled napps folder."""
#        folder = self._enabled
#        napps = []
#        ignored_paths = set(['.installed', '__pycache__', '__init__.py'])
#        for username in set(listdir(folder)) - ignored_paths:
#            username_dir = path.join(folder, username)
#            for napp_name in set(listdir(username_dir)) - ignored_paths:
#                napps.append((username, napp_name))
#        return sorted(napps)
