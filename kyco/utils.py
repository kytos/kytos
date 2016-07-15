"""Utilities"""

import logging

from abc import abstractmethod, ABCMeta

from kyco.core.events import KycoNullEvent
from kyco.core.exceptions import KycoNAppMissingInitArgument

log = logging.getLogger('kytos[A]')

APP_MSG = "[App %s] %s | ID: %02d | R: %02d | P: %02d | F: %s"


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


class KycoCoreNApp(metaclass=ABCMeta):
    """Base class for any KycoNApp to be developed."""

    msg_in_buffer = False
    msg_out_buffer = False
    app_buffer = False

    def __init__(self, **kwargs):
        """Go through all of the instance methods and selects those that have
        the events attribute, then creates a dict containing the event_name
        and the list of methods that are responsible for handling such event.

        At the end, the setUp method is called as a complement of the init
        process.
        """
        self._listeners = {}
        self.events_buffer = None

        handler_methods = [getattr(self, method_name) for method_name in
                           dir(self) if method_name[0] != '_' and
                           callable(getattr(self, method_name)) and
                           hasattr(getattr(self, method_name), 'events')]

        for method in handler_methods:
            for event_name in method.events:
                if event_name not in self._listeners:
                    self._listeners[event_name] = []
                self._listeners[event_name].append(method)

        if self.msg_in_buffer:
            if 'add_to_msg_in_buffer' not in kwargs:
                raise KycoNAppMissingInitArgument('add_to_msg_in_buffer')
            self.add_to_msg_in_buffer = kwargs['add_to_msg_in_buffer']

        if self.msg_out_buffer:
            if 'add_to_msg_out_buffer' not in kwargs:
                raise KycoNAppMissingInitArgument('add_to_msg_out_buffer')
            self.add_to_msg_out_buffer = kwargs['add_to_msg_out_buffer']

        if self.app_buffer:
            if 'add_to_app_buffer' not in kwargs:
                raise KycoNAppMissingInitArgument('add_to_app_buffer')
            self.add_to_app_buffer = kwargs['add_to_app_buffer']

        self.set_up(**kwargs)
        log.info("Instance of {} created.", self.name)

    @abstractmethod
    def set_up(self, **kwargs):
        """'Replaces' the 'init' method for the KycoApp subclass.

        The setUp method is automatically called by the __init__ method.
        Users shouldn't call this method."""
        pass

    @abstractmethod
    def shutdown(self):
        """This method will be called before the app is unloaded of
        before the controller is stopped"""
        pass


class KycoNApp(metaclass=ABCMeta):
    """Base class for any KycoNApp to be developed."""

    msg_out_buffer = False
    app_buffer = False

    def __init__(self, **kwargs):
        """Go through all of the instance methods and selects those that have
        the events attribute, then creates a dict containing the event_name
        and the list of methods that are responsible for handling such event.

        At the end, the setUp method is called as a complement of the init
        process.
        """
        self._listeners = {}
        self.events_buffer = None

        handler_methods = [getattr(self, method_name) for method_name in
                           dir(self) if method_name[0] != '_' and
                           callable(getattr(self, method_name)) and
                           hasattr(getattr(self, method_name), 'events')]

        for method in handler_methods:
            for event_name in method.events:
                if event_name not in self._listeners:
                    self._listeners[event_name] = []
                self._listeners[event_name].append(method)

        if self.msg_out_buffer:
            if 'add_to_msg_out_buffer' not in kwargs:
                raise KycoNAppMissingInitArgument('add_to_msg_out_buffer')
            self.add_to_msg_out_buffer = kwargs['add_to_msg_out_buffer']

        if self.app_buffer:
            if 'add_to_app_buffer' not in kwargs:
                raise KycoNAppMissingInitArgument('add_to_app_buffer')
            self.add_to_app_buffer = kwargs['add_to_app_buffer']

        self.set_up(**kwargs)
        log.info("Instance of {} created.", self.name)

    @abstractmethod
    def set_up(self, **kwargs):
        """'Replaces' the 'init' method for the KycoApp subclass.

        The setUp method is automatically called by the __init__ method.
        Users shouldn't call this method."""
        pass

    @abstractmethod
    def shutdown(self):
        """This method will be called before the app is unloaded of
        before the controller is stopped"""
        pass


class ListenTo(object):
    """Decorator for Event Listeners methods.

    This decorator should be used on methods, inside an APP, to define which
    type of event the method will handle. With this, we will be able to
    'schedule' the app/method to receive an event when a new event is
    registered on the controller buffers.

    The decorator will add an attribute to the method called 'events', that
    will be a list of the events that the method will handle.

    Example of usage:

    .. code-block:: python3

        class MyAppClass(KycoApp):
            @listen_to('KycoMessageIn')
            def my_handler_of_message_in(self, event):
                # Do stuff here...

            @listen_to('KycoMessageOut')
            def my_handler_of_message_out(self, event):
                # Do stuff here...

            @listen_to('KycoMessageIn', 'KycoMessageOut')
            def my_stats_handler_of_any_message(self, event):
                # Do stuff here...
    """
    def __init__(self, event, *events):
        """Initial setup of handler methods.

        This will be called when the class is created.
        It need to have at least one event type (as string).

        Args:
            event (str): String with the name of a event to be listened to.
            events (str): other events to be listened to.
        """
        if callable(event):
            raise Exception("You need to pass at least one eventType")
        self.events = [event]
        self.events.extend(events)

    def __call__(self, handler):
        """Just return the handler method with the events attribute"""
        def wrapped_func(*args):
            if isinstance(args[0], KycoNullEvent):
                return None
            return handler(*args)
        wrapped_func.events = self.events
        return wrapped_func
