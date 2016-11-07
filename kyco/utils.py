"""Utilities"""
import logging
from datetime import datetime, timezone
from threading import Thread

__all__ = ('listen_to', 'now', 'run_on_thread',
           'start_logger')

# APP_MSG = "[App %s] %s | ID: %02d | R: %02d | P: %02d | F: %s"


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


def start_logger(name):
    """Starts the loggers, both the Kyco and the KycoNApp"""
    fmt = '%(asctime)s - %(levelname)s [%(name)s] (%(threadName)s) %(message)s'
    # fmt += '\n           %(module)s - %(funcName)s - %(lineno)d'
    logging.basicConfig(format=fmt, level=logging.INFO)
    return logging.getLogger(name)
