"""Kytos Napps Module."""
import json
import os
import sys
from abc import ABCMeta, abstractmethod
from threading import Event, Thread

from kytos.core.logs import NAppLog
from kytos.core.helpers import listen_to

__all__ = 'KytosNApp',

log = NAppLog()


class KytosNApp(Thread, metaclass=ABCMeta):
    """Base class for any KytosNApp to be developed."""

    __event = Event()

    def __init__(self, controller, **kwargs):
        """Contructor of KytosNapps.

        Go through all of the instance methods and selects those that have
        the events attribute, then creates a dict containing the event_name
        and the list of methods that are responsible for handling such event.

        At the end, the setUp method is called as a complement of the init
        process.
        """
        Thread.__init__(self, daemon=False)
        self.controller = controller
        self._listeners = {'kytos/core.shutdown': [self._shutdown_handler]}
        #: int: Seconds to sleep before next call to :meth:`execute`. If
        #: negative, run :meth:`execute` only once.
        self.__interval = -1

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

        self.load_json()

    def load_json(self):
        """Method used to update object attributes based on kytos.json."""
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
        """Call the setup and the execute method.

        It should not be overriden.
        """
        log.info("Running %s App", self.name)
        # TODO: If the setup method is blocking, then the execute method will
        #       never be called. Should we execute it inside a new thread?
        self.setup()
        self.execute()
        while self.__interval > 0 and not self.__event.is_set():
            self.__event.wait(self.__interval)
            self.execute()

    @listen_to('kytos/core.shutdown')
    def _shutdown_handler(self, event):
        """Method used to listen shutdown event from kytos.

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

        The setup method is automatically called by the run method.
        Users shouldn't call this method directly.
        """
        pass

    @abstractmethod
    def execute(self):
        """Execute in a loop until the signal 'kytos/core.shutdown' is received.

        The execute method is called by KytosNApp class.
        Users shouldn't call this method directly.
        """
        pass

    @abstractmethod
    def shutdown(self):
        """Called before the app is unloaded, before the controller is stopped.

        The user implementation of this method should do the necessary routine
        for the user App and also it is a good moment to break the loop of the
        execute method if it is in a loop.

        This methods is not going to be called directly, it is going to be
        called by the _shutdown_handler method when a KytosShutdownEvent is
        sent.
        """
        pass
