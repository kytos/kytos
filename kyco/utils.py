"""Utilities"""

import logging

from abc import abstractmethod, ABCMeta


APP_MSG = "[App %s] %s | ID: %02d | R: %02d | P: %02d | F: %s"


def start_logger():
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


class KycoApp(metaclass=ABCMeta):
    _listeners = {'msg_in_event': None,
                  'msg_out_event': None,
                  'apps_event': None}
    def __init__(self):
        # Get all methods from the instance
        # check which one has a attribute named 'event_type'
        # register this method on the '_listeners' dict
        # of the instance
        pass

    @abstractmethod
    def setUp():
        pass






class listen_to(object):
    """Decorator for App Events Listener"""
    def __init__(self, event, *events):
        if callable(event):
            raise Exception("You need to pass at least one eventType")
        self.events = [event]
        self.events.extend(events)

    def __call__(self, f):

        def wrapped_func(*args):
            return f(*args)
        wrapped_func.events = self.events
        return wrapped_func


class ExampleApp(KycoApp):
    def setUp(self):
        self.nome = "APP"

    @listen_to('KycoMessageIn', 'KycoMessageOut', 'NewAppLoaded')
    def test(self, event):
        print(event)
