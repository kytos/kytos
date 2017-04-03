"""Module with classes used to handle logs displayed by Kytos SDN Platform."""
import logging
from logging.handlers import SysLogHandler

__all__ = ('LogManager')


class LogManager:
    """Class responsible to handle all logs send by kytos and the Napps."""

    fmt = '%(asctime)s - %(levelname)s [%(name)s] (%(threadName)s) %(message)s'
    handlers_enabled = []
    loggers = {}

    def __init__(self, mode='INFO'):
        """Contructor of LogManager.

        This method will create a LogManager instance with the mode given.

        Args:
            mode(string): Type of log that will be registered by kytos.
        """
        logging.basicConfig(format=self.fmt, level=getattr(logging, mode))

    def new_logger(self, logger_name):
        """Method used to instantiate a new logger.

        Args:
            logger_name(string): logger name that will be instantiated.
        Returns:
            logger(`logging.Logger`): instance of logging.Logger.
        """
        logger = logging.getLogger(logger_name)
        if logger_name not in self.loggers.keys():
            self.loggers[logger.name] = logger
            self.__add_handlers_enabled_to_logger(logger)

        return logger

    def __add_handlers_enabled_to_logger(self, logger):
        """Private method to add all handlers in a logger instance.

        Args:
            logger(`logging.Logger`): instance that will receive the handlers.
        """
        for handler in self.handlers_enabled:
            logger.addHandler(handler)

    def __add_handler_to_loggers(self, handler):
        """"Private method to add a new handlers into all loggers instances.

        Args:
            handler(Handler): instance of Handler
        """
        for logger in self.loggers.values():
            logger.addHandler(handler)

        self.handlers_enabled.append(handler)

    def enable_syslog(self):
        """Method used to enable the syslog."""
        syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
        syslog_handler.setFormatter(logging.Formatter(self.fmt))
        self.__add_handler_to_loggers(syslog_handler)
        self.syslog = True

    def enable_websocket_log(self, websocket):
        """Method used used to enable the websocket log.

        This method get the stream from websocket given and add this into the
        handlers registered.

        Args:
            websocket(LogWebSocket): instance of LogWebSocket.
        """
        stream_handler = logging.StreamHandler(websocket.stream)
        stream_handler.setFormatter(logging.Formatter(self.fmt))
        self.__add_handler_to_loggers(stream_handler)

    def __hide_unused_logs(self):
        """Privated method used to hide unused logs."""
        engineio_logs = logging.getLogger('engineio')
        engineio_logs.setLevel(logging.NOTSET)
        socketio_logs = logging.getLogger('socketio')
        socketio_logs.setLevel(logging.NOTSET)
