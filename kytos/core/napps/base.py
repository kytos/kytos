"""Kytos Napps Module."""
import json
import os
import re
import sys
import tarfile
import urllib
from abc import ABCMeta, abstractmethod
from pathlib import Path
from random import randint
from threading import Event, Thread

from kytos.core.logs import NAppLog

__all__ = ('KytosNApp',)

LOG = NAppLog()


class NApp:
    """Class to represent a NApp."""

    # pylint: disable=too-many-arguments
    def __init__(self, username=None, name=None, version=None,
                 repository=None, meta=False):
        self.username = username
        self.name = name
        self.version = version if version else 'latest'
        self.repository = repository
        self.meta = meta
        self.description = None
        self.tags = []
        self.enabled = False
        self.napp_dependencies = []

    def __str__(self):
        return "{}/{}".format(self.username, self.name)

    def __repr__(self):
        return f"NApp({self.username}/{self.name})"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        """Compare username/name strings."""
        return isinstance(other, self.__class__) and self.id == other.id

    @property
    def id(self):  # pylint: disable=invalid-name
        """username/name string."""
        return str(self)

    @property
    def uri(self):
        """Return a unique identifier of this NApp."""
        version = self.version if self.version else 'latest'

        if not self._has_valid_repository():
            return ""

        # Use the next line after Diraol fix redirect using ":" for version
        # return "{}/{}:{}".format(self.repository, self.id, version)

        return "{}/{}-{}".format(self.repository, self.id, version)

    @property
    def package_url(self):
        """Return a fully qualified URL for a NApp package."""
        if not self.uri:
            return ""
        return "{}.napp".format(self.uri)

    @classmethod
    def create_from_uri(cls, uri):
        """Return a new NApp instance from an unique identifier."""
        regex = r'^(((https?://|file://)(.+))/)?(.+?)/(.+?)/?(:(.+))?$'
        match = re.match(regex, uri)

        if not match:
            return None

        return cls(username=match.groups()[4],
                   name=match.groups()[5],
                   version=match.groups()[7],
                   repository=match.groups()[1])

    @classmethod
    def create_from_json(cls, filename):
        """Return a new NApp instance from a metadata file."""
        with open(filename, encoding='utf-8') as data_file:
            data = json.loads(data_file.read())

        return cls.create_from_dict(data)

    @classmethod
    def create_from_dict(cls, data):
        """Return a new NApp instance from metadata."""
        napp = cls()

        for attribute, value in data.items():
            setattr(napp, attribute, value)

        return napp

    def as_json(self):
        """Dump all NApp attributes on a json format."""
        return json.dumps(self.__dict__)

    def match(self, pattern):
        """Whether a pattern is present on NApp id, description and tags."""
        try:
            pattern = '.*{}.*'.format(pattern)
            pattern = re.compile(pattern, re.IGNORECASE)
            strings = [self.id, self.description] + self.tags
            return any(pattern.match(string) for string in strings)
        except TypeError:
            return False

    def download(self):
        """Download NApp package from his repository.

        Raises:
            urllib.error.HTTPError: If download is not successful.

        Returns:
            str: Downloaded temp filename.

        """
        if not self.package_url:
            return None

        package_filename = urllib.request.urlretrieve(self.package_url)[0]
        extracted = self._extract(package_filename)
        Path(package_filename).unlink()
        self._update_repo_file(extracted)
        return extracted

    @staticmethod
    def _extract(filename):
        """Extract NApp package to a temporary folder.

        Return:
            pathlib.Path: Temp dir with package contents.
        """
        random_string = '{:0d}'.format(randint(0, 10**6))
        tmp = '/tmp/kytos-napp-' + Path(filename).stem + '-' + random_string
        os.mkdir(tmp)
        with tarfile.open(filename, 'r:xz') as tar:
            tar.extractall(tmp)
        return Path(tmp)

    def _has_valid_repository(self):
        """Whether this NApp has a valid repository or not."""
        return all([self.username, self.name, self.repository])

    def _update_repo_file(self, destination=None):
        """Create or update the file '.repo' inside NApp package."""
        with open("{}/.repo".format(destination), 'w') as repo_file:
            repo_file.write(self.repository + '\n')


class KytosNApp(Thread, metaclass=ABCMeta):
    """Base class for any KytosNApp to be developed."""

    def __init__(self, controller, **kwargs):
        """Contructor of KytosNapps.

        Go through all of the instance methods and selects those that have
        the events attribute, then creates a dict containing the event_name
        and the list of methods that are responsible for handling such event.

        At the end, the setup method is called as a complement of the init
        process.
        """
        Thread.__init__(self, daemon=False)
        self.controller = controller
        self.username = None  # loaded from json
        self.name = None      # loaded from json
        self.meta = False     # loaded from json
        self._load_json()

        # Force a listener with a private method.
        self._listeners = {
            'kytos/core.shutdown': [self._shutdown_handler],
            'kytos/core.shutdown.' + self.napp_id: [self._shutdown_handler]}

        self.__event = Event()
        #: int: Seconds to sleep before next call to :meth:`execute`. If
        #: negative, run :meth:`execute` only once.
        self.__interval = -1
        self.setup()

        #: Add non-private methods that listen to events.
        handler_methods = [getattr(self, method_name) for method_name in
                           dir(self) if method_name[0] != '_' and
                           callable(getattr(self, method_name)) and
                           hasattr(getattr(self, method_name), 'events')]

        # Building the listeners dictionary
        for method in handler_methods:
            for event_name in method.events:
                if event_name not in self._listeners:
                    self._listeners[event_name] = []
                self._listeners[event_name].append(method)

    @property
    def napp_id(self):
        """username/name string."""
        return "{}/{}".format(self.username, self.name)

    def listeners(self):
        """Return all listeners registered."""
        return list(self._listeners.keys())

    def _load_json(self):
        """Update object attributes based on kytos.json."""
        current_file = sys.modules[self.__class__.__module__].__file__
        json_path = os.path.join(os.path.dirname(current_file), 'kytos.json')
        with open(json_path, encoding='utf-8') as data_file:
            data = json.loads(data_file.read())

        for attribute, value in data.items():
            setattr(self, attribute, value)

    def execute_as_loop(self, interval):
        """Run :meth:`execute` within a loop. Call this method during setup.

        By calling this method, the application does not need to worry about
        loop details such as sleeping and stopping the loop when
        :meth:`shutdown` is called. Just call this method during :meth:`setup`
        and implement :meth:`execute` as a single execution.

        Args:
            interval (int): Seconds between each call to :meth:`execute`.
        """
        self.__interval = interval

    def run(self):
        """Call the execute method, looping as needed.

        It should not be overriden.
        """
        LOG.info("Running NApp: %s", self)
        self.execute()
        while self.__interval > 0 and not self.__event.is_set():
            self.__event.wait(self.__interval)
            self.execute()

    # all listeners receive event
    def _shutdown_handler(self, event):  # pylint: disable=unused-argument
        """Listen shutdown event from kytos.

        This method listens the kytos/core.shutdown event and call the shutdown
        method from napp subclass implementation.

        Paramters
            event (:class:`KytosEvent`): event to be listened.
        """
        if not self.__event.is_set():
            self.__event.set()
            self.shutdown()

    @abstractmethod
    def setup(self):
        """Replace the 'init' method for the KytosApp subclass.

        The setup method is automatically called on the NApp __init__().
        Users aren't supposed to call this method directly.
        """
        pass

    @abstractmethod
    def execute(self):
        """Execute in a loop until 'kytos/core.shutdown' is received.

        The execute method is called by KytosNApp class.
        Users shouldn't call this method directly.
        """
        pass

    @abstractmethod
    def shutdown(self):
        """Run before the app is unloaded and the controller, stopped.

        The user implementation of this method should do the necessary routine
        for the user App and also it is a good moment to break the loop of the
        execute method if it is in a loop.

        This methods is not going to be called directly, it is going to be
        called by the _shutdown_handler method when a KytosShutdownEvent is
        sent.
        """
        pass
