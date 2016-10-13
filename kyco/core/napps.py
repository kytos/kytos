import logging

from abc import ABCMeta, abstractmethod
from threading import Event, Thread

from kyco.utils import listen_to

log = logging.getLogger('Kyco')

__all__ = ('KycoCoreNApp', 'KycoNApp')

class KycoNApp(Thread, metaclass=ABCMeta):
    """Base class for any KycoNApp to be developed."""
    __event = Event()
    EXECUTE_INTERVAL = 30

    def __init__(self, controller, **kwargs):
        """Go through all of the instance methods and selects those that have
        the events attribute, then creates a dict containing the event_name
        and the list of methods that are responsible for handling such event.

        At the end, the setUp method is called as a complement of the init
        process.
        """
        Thread.__init__(self, daemon=False)
        self.controller = controller
        self._listeners = {'kyco/core.shutdown': [self._shutdown_handler]}

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

        # TODO: Load NApp data based on its json file
        # self.name is already used in Thread class. Other attribute should be
        # used

    def run(self):
        """This method will call the setup and the execute methos.

        It should not be overriden."""
        log.info("Running %s App", self.name)
        # TODO: If the setup method is blocking, then the execute method will
        #       never be called. Should we execute it inside a new thread?
        self.setup()
        self._execute_loop()

    @listen_to('kyco/core.shutdown')
    def _shutdown_handler(self, event):
        self.__event.set()
        self.shutdown()

    def _execute_loop(self):
        while(not self.__event.is_set()):
            self.execute()
            self.__event.wait(self.EXECUTE_INTERVAL)

    @abstractmethod
    def setup(self):
        """'Replaces' the 'init' method for the KycoApp subclass.

        The setup method is automatically called by the run method.
        Users shouldn't call this method directly."""
        pass

    @abstractmethod
    def execute(self):
        """Method executed in a loop until the signal 'kyco/core.shutdown'
        is received.

        The execute method is called by KycoNApp class.
        Users shouldn't call this method directly."""
        pass

    @abstractmethod
    def shutdown(self):
        """Called before the app is unloaded, before the controller is stopped.

        The user implementation of this method should do the necessary routine
        for the user App and also it is a good moment to break the loop of the
        execute method if it is in a loop.

        This methods is not going to be called directly, it is going to be
        called by the _shutdown_handler method when a KycoShutdownEvent is
        sent."""
        pass


class KycoCoreNApp(KycoNApp):
    """Base class for any KycoCoreNApp to be developed."""
    pass
