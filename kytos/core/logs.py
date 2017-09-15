"""Handle logs displayed by Kytos SDN Platform."""
import inspect
import logging
import re
from configparser import RawConfigParser
# noqa so it does not conflict with grouped imports
# pylint: disable=ungrouped-imports
from logging import Formatter, config, getLogger
# pylint: enable=ungrouped-imports
from pathlib import Path

from kytos.core.websocket import WebSocketHandler

__all__ = ('LogManager', 'NAppLog')
LOG = getLogger(__name__)


class LogManager:
    """Manage handlers for all loggers."""

    _PARSER = RawConfigParser()
    _DEFAULT_FMT = 'formatter_console'

    @classmethod
    def load_config_file(cls, config_file, debug='False'):
        """Load log configuration file.

        Check whether file exists and if there's an OSError, try removing
        syslog handler.

        Args:
            config_file (:class:`str`, :class:`pathlib.Path`):
                Configuration file path.
        """
        if Path(config_file).exists():
            cls._PARSER.read(config_file)
            cls._set_debug_mode(debug)
            cls._use_config_file(config_file)
        else:
            LOG.warning('Log config file "%s" does not exist. Using default '
                        'Python logging configuration.',
                        config_file)

    @classmethod
    def _set_debug_mode(cls, debug=False):
        if debug is True:
            cls._PARSER.set('logger_root', 'level', 'DEBUG')
            cls._PARSER.set('logger_api_server', 'level', 'DEBUG')
            LOG.info('Setting log configuration with debug mode.')

    @classmethod
    def _use_config_file(cls, config_file):
        """Use parsed logging configuration."""
        try:
            config.fileConfig(cls._PARSER, disable_existing_loggers=False)
            LOG.info('Logging config file "%s" loaded successfully.',
                     config_file)
        except OSError:
            cls._catch_config_file_exception(config_file)

    @classmethod
    def _catch_config_file_exception(cls, config_file):
        """Try not using syslog handler (for when it is not installed)."""
        if 'handler_syslog' in cls._PARSER:
            LOG.warning('Failed to load "%s". Trying to disable syslog '
                        'handler.', config_file)
            cls._PARSER.remove_section('handler_syslog')
            cls._use_config_file(config_file)
        else:
            LOG.warning('Failed to load "%s". Using default Python '
                        'logging configuration.', config_file)

    @classmethod
    def enable_websocket(cls, socket):
        """Output logs to a web socket.

        Args:
            socket: socketio's socket.

        Returns:
            logging.StreamHandler: Handler with the socket as stream.

        """
        handler = WebSocketHandler.get_handler(socket)
        cls.add_handler(handler)
        return handler

    @classmethod
    def add_handler(cls, handler):
        """Add handler to loggers.

        Use formatter_console if it exists.

        Args:
            handler (:mod:`logging.handlers`): Handle to be added.
        """
        if cls._PARSER.has_section(cls._DEFAULT_FMT):
            fmt_conf = cls._PARSER[cls._DEFAULT_FMT]
            fmt = Formatter(fmt_conf.get('format', None),
                            fmt_conf.get('datefmt', None))
            handler.setFormatter(fmt)
        handler.addFilter(cls.filter_session_disconnected)
        getLogger().addHandler(handler)

    @staticmethod
    def filter_session_disconnected(record):
        """Remove harmless session disconnected error.

        Despite this error, everything seems to be working. As we can't catch
        it anywhere, we filter it.
        """
        msg_end = "KeyError: 'Session is disconnected'"
        return not (record.name == 'werkzeug' and record.levelname == 'ERROR'
                    and record.args and isinstance(record.args[0], str)
                    and record.args[0].endswith(msg_end))


# Add filter to all pre-existing handlers
HANDLER_FILTER = LogManager.filter_session_disconnected
for root_handler in logging.root.handlers:
    if HANDLER_FILTER not in root_handler.filters:
        root_handler.addFilter(HANDLER_FILTER)


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
        napp_id = _detect_napp_id()
        logger = getLogger(napp_id)
        return logger.__getattribute__(name)


#: Detect NApp ID from filename
NAPP_ID_RE = re.compile(r'.*napps/(.*?)/(.*?)/')


def _detect_napp_id():
    """Get the last called NApp in caller's stack.

    We use the last innermost NApp because a NApp *A* may call a NApp *B* and,
    when *B* uses the logger, the logger's name should be *B*.

    Returns:
        str, None: NApp ID or None if no NApp is found in the caller's stack.

    """
    for frame in inspect.stack():
        if not frame.filename == __file__:
            match = NAPP_ID_RE.match(frame.filename)
            if match:
                return '/'.join(match.groups())
    return None
