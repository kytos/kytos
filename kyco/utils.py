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
    def __init__(self):
		"""
			Go through all of the instance methods and selects those that have 
			the events attribute, then creates a dict containing the event_name
			and the list of methods that are responsible for handling such event
		"""
    	self._listeners = {}

		handler_methods = [getattr(self,method_name) for method_name in 
						   dir(self) if callable(getattr(self,method_name))
						   and hasattr(method_name,'events')]
		
		for method in handler_methods:
			for event_name in method.events:
				if event_name not in self._listeners:
					self._listeners[event_name] = []
				self._listeners[event_name].append(method)


    @abstractmethod
    def setUp(self):
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
