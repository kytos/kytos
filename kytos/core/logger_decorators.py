"""Decorators for the logger class."""
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

from kytos.core.apm import begin_span


def queue_decorator(klass):
    """Decorates the logger class so it uses queues internally"""
    class QueueLogger(klass):
        """Logger class decorated to use queues internally"""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.queue = Queue()
            self.listener = QueueListener(self.queue,
                                          respect_handler_level=True)
            self.listener.start()
            super().addHandler(QueueHandler(self.queue))

        def _change_handlers(self, *hdlrs):
            """Set the handlers of the queue listener"""
            self.listener.stop()
            self.listener = QueueListener(self.queue, *hdlrs,
                                          respect_handler_level=True)
            self.listener.start()

        # pylint: disable=invalid-name
        def addHandler(self, hdlr):
            """Add a handler to the queue listener"""
            old_handlers = self.listener.handlers
            self._change_handlers(*old_handlers, hdlr)

        def removeHandler(self, hdlr):
            """Remove a handler from the queue listener"""
            old_handlers = self.listener.handlers
            new_handlers = [handler for handler in old_handlers
                            if handler is not hdlr]
            self._change_handlers(*new_handlers)

        def hasHandlers(self):
            """Check if the queue listener has any handlers"""
            if self.listener.handlers:
                return True
            if self.propagate and self.parent:
                return self.parent.hasHandlers()
            return False
        # pylint: disable=invalid-name

    return QueueLogger


def apm_decorator(klass):
    """Decorates the logger class for performance monitoring"""
    class APMLogger(klass):
        """Logger class decorated for log performance monitoring"""
        pass

    for func_name in ['debug', 'info', 'warning',
                      'error', 'exception', 'critical',
                      'fatal', 'log']:
        setattr(APMLogger, func_name,
                begin_span(getattr(klass, func_name), 'logging'))

    return APMLogger


def root_decorator(klass):
    """Decorator for turning a logger class into a root logger class"""
    class RootLogger(klass):
        """
        A root logger is not that different to any other logger, except that
        it must have a logging level and there is only one instance of it in
        the hierarchy.
        """
        def __init__(self, level):
            """
            Initialize the logger with the name "root".
            """
            super().__init__("root", level)

        def __reduce__(self):
            return logging.getLogger, ()

    return RootLogger
