"""Utilities"""

import logging

from abc import abstractmethod, ABCMeta
from datetime import datetime, timezone
from threading import Thread

__all__ = ('KycoCoreNApp', 'KycoNApp', 'listen_to', 'now', 'run_on_thread',
           'start_logger')

log = logging.getLogger('kytos[A]')

APP_MSG = "[App %s] %s | ID: %02d | R: %02d | P: %02d | F: %s"

def listen_to(event, *events):
    """Decorator for Event Listener methods.

    This decorator was built to be used on NAPPs methods to define which
    type of event the method will handle. With this, we will be able to
    'schedule' the app/method to receive an event when a new event is
    registered on the controller buffers.
    By using the run_on_thread decorator, we also guarantee that the method
    (handler) will be called from inside a new thread, avoiding this method to
    block its caller.

    The decorator will add an attribute to the method called 'events', that
    will be a list of the events that the method will handle.

    The event that will be listened to is always a string, but it can represent
    a regular expression to match against multiple Event Types.

    Example of usage:

    .. code-block:: python3

        class MyAppClass(KycoApp):
            @listen_to('KycoMessageIn')
            def my_handler_of_message_in(self, event):
                # Do stuff here...

            @listen_to('KycoMessageOut')
            def my_handler_of_message_out(self, event):
                # Do stuff here...

            @listen_to('KycoMessageInHello', 'KycoMessageOutHello')
            def my_handler_of_hello_messages(self, event):
                # Do stuff here...

            @listen_to('KycoMessage*Hello')
            def my_other_handler_of_hello_messages(self, event):
                # Do stuff here...

            @listen_to('KycoMessage*Hello')
            def my_handler_of_hello_messages(self, event):
                # Do stuff here...

            @listen_to('KycoMessage*')
            def my_stats_handler_of_any_message(self, event):
                # Do stuff here...
    """
    def decorator(handler):
        """Decorate the handler method.

        Returns:
            A method with a `events` attribute (list of events to be listened)
            and also decorated to run on a new thread.
        """
        @run_on_thread
        def threaded_handler(*args):
            """Decorating the handler to run from a new thread"""
            handler(*args)

        threaded_handler.events = [event]
        threaded_handler.events.extend(events)
        return threaded_handler

    return decorator


def now(tzone=timezone.utc):
    """Returns the current datetime (default to UTC)"""
    return datetime.now(tzone)


def run_on_thread(method):
    """Decorator to run the decorated method inside a new thread

    Returns:
        Decorated method that will run inside a new thread.
        When the decorated method is called, it will not return the created
        thread to the caller.
    """
    def threaded_method(*args):
        """Ensure the handler method runs inside a new thread"""
        thread = Thread(target=method, args=args)
        thread.start()
    return threaded_method


def start_logger():
    """Starts the loggers, both the Kyco and the KycoNApp"""
    general_formatter = logging.Formatter('%(asctime)s - %(levelname)s '
                                          '[%(name)s] %(message)s')
    app_formatter = logging.Formatter('%(asctime)s - %(levelname)s '
                                      '[%(name)s] %(message)s')

    controller_console_handler = logging.StreamHandler()
    controller_console_handler.setLevel(logging.DEBUG)
    controller_console_handler.setFormatter(general_formatter)

    app_console_handler = logging.StreamHandler()
    app_console_handler.setLevel(logging.DEBUG)
    app_console_handler.setFormatter(app_formatter)

    controller_log = logging.getLogger('Kyco')
    controller_log.setLevel(logging.DEBUG)
    controller_log.addHandler(controller_console_handler)

    app_log = logging.getLogger('KycoNApp')
    app_log.setLevel(logging.DEBUG)
    app_log.addHandler(app_console_handler)

    return controller_log


class KycoNApp(Thread, metaclass=ABCMeta):
    """Base class for any KycoNApp to be developed."""

    def __init__(self, controller, **kwargs):
        """Go through all of the instance methods and selects those that have
        the events attribute, then creates a dict containing the event_name
        and the list of methods that are responsible for handling such event.

        At the end, the setUp method is called as a complement of the init
        process.
        """
        Thread.__init__(self, daemon=False)
        self._listeners = {'KycoShutdownEvent': [self._shutdown_handler]}
        self.controller = controller

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
        self.name = None

    def run(self):
        """This method will call the setup and the execute methos.

        It should not be overriden."""
        log.info("Running %s App", self.name)
        # TODO: If the setup method is blocking, then the execute method will
        #       never be called. Should we execute it inside a new thread?
        self.setup()
        self.execute()

    @listen_to('KycoShutdownEvent')
    def _shutdown_handler(self, event):
        self.shutdown()

    @abstractmethod
    def setup(self):
        """'Replaces' the 'init' method for the KycoApp subclass.

        The setup method is automatically called by the run method.
        Users shouldn't call this method directly."""
        pass

    @abstractmethod
    def execute(self):
        """Method to be runned once on app 'start' or in a loop.

        The execute method is called by the run method of KycoNApp class.
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
