"""Handle logs displayed by Kytos SDN Platform."""
import inspect
import logging
import logging.handlers
import re

__all__ = 'LogManager', 'NAppLog'

FORMAT = '%(asctime)s - %(levelname)s [%(name)s] (%(threadName)s) %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)


class LogManager:
    """Manage handlers for all loggers."""

    @classmethod
    def add_syslog(cls):
        """Output all logs to syslog."""
        handler = logging.handlers.SysLogHandler(address='/dev/log')
        cls._add_handler(handler)
        return handler

    @classmethod
    def add_stream_handler(cls, stream):
        """Output all logs to the given stream.

        Args:
            stream: Object that supports ``write()`` and ``flush()``.
        """
        handler = logging.StreamHandler(stream)
        cls._add_handler(handler)
        return handler

    @staticmethod
    def _add_handler(handler):
        handler.setFormatter(logging.Formatter(FORMAT))
        logging.getLogger().addHandler(handler)


class NAppLog:
    """High-level logger for NApp devs.

    From NApp dev's point of view:
    - No need for instantiation
    - Logger name is automatically assigned

    Redirect all calls to a logger with the correct name (NApp ID).

    The appropriate logger is a logging.Logger with NApp ID as its name. If no
    NApp is found, use the root logger.

    As any NApp can use this logger, its name is detected in every call by
    inspecting the caller's stack. If no NApp is found, use the root logger.
    """

    def __getattribute__(self, name):
        """Detect NApp ID and use its logger."""
        napp_id = detect_napp_id()
        logger = logging.getLogger(napp_id)
        return logger.__getattribute__(name)


#: Detect NApp ID from filename
NAPP_ID_RE = re.compile(r'.*napps/(.*?)/(.*?)/')


def detect_napp_id():
    """Get the last called NApp in caller's stack.

    We use the last innermost NApp because a NApp *A* may call a NApp *B* and,
    when *B* uses the logger, the logger's name should be *B*.

    Returns:
        str: NApp ID.
        None: If no NApp is found in the caller's stack.
    """
    for frame in inspect.stack():
        if not frame.filename == __file__:
            match = NAPP_ID_RE.match(frame.filename)
            if match:
                return '/'.join(match.groups())
    return None
