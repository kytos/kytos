"""Module to monitor installed napps."""
import logging
import re
from pathlib import Path

from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import Observer

LOG = logging.getLogger(__name__)


class NAppDirListener(RegexMatchingEventHandler):
    """Class to handle directory changes."""

    regexes = [re.compile(r".*\/kytos\/napps\/[a-zA-Z][^/]+\/[a-zA-Z].*")]
    ignore_regexes = [re.compile(r".*\.installed")]
    _controller = None

    def __init__(self, controller):
        """Require controller to get NApps dir, load and unload NApps.

        In order to watch the NApps dir for modifications, it must be created
        if it doesn't exist (in this case, kytos-utils has not been run before
        kytosd). We use the same dir permissions as in kytos-utils.

        Args:
            controller(kytos.core.controller): A controller instance.
        """
        super().__init__()
        self._controller = controller
        self.napps_path = self._controller.options.napps
        mode = 0o777 if self.napps_path.startswith('/var') else 0o755
        Path(self.napps_path).mkdir(mode=mode, parents=True, exist_ok=True)
        self.observer = Observer()

    def start(self):
        """Start handling directory changes."""
        self.observer.schedule(self, self.napps_path, True)
        self.observer.start()
        LOG.info('NAppDirListener Started...')

    def stop(self):
        """Stop handling directory changes."""
        self.observer.stop()
        LOG.info('NAppDirListener Stopped...')

    def _get_napp(self, absolute_path):
        """Get a username and napp_name from absolute path.

        Args:
            absolute_path(str): String with absolute path.

        Returns:
            tuple: Tuple with username and napp_name.

        """
        relative_path = absolute_path.replace(self.napps_path, '')
        return tuple(relative_path.split('/')[1:3])

    def on_created(self, event):
        """Load a napp from created directory.

        Args:
            event(watchdog.events.DirCreatedEvent): Event received from an
                observer.
        """
        napp = self._get_napp(event.src_path)
        LOG.debug('The NApp "%s/%s" was enabled.', *napp)
        self._controller.load_napp(*napp)

    def on_deleted(self, event):
        """Unload a napp from deleted directory.

        Args:
            event(watchdog.events.DirDeletedEvent): Event received from an
                observer.
        """
        napp = self._get_napp(event.src_path)
        LOG.debug('The NApp "%s/%s" was disabled.', *napp)
        self._controller.unload_napp(*napp)
