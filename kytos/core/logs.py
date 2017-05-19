"""Handle logs displayed by Kytos SDN Platform."""
import inspect
import re
from configparser import RawConfigParser
from logging import Formatter, StreamHandler, config, getLogger
from pathlib import Path

__all__ = ('LogManager', 'NAppLog')


class LogManager:
    """Manage handlers for all loggers."""

    _CONFIG = RawConfigParser()
    _DEFAULT_FMT = 'formatter_console'

    @classmethod
    def load_logging_file(cls, config_file):
        """Load log configuration file.

        Args:
           config_file (str, Path): Configuration file path.
        """
        config_file = Path(config_file)
        if config_file.exists():
            config.fileConfig(config_file, disable_existing_loggers=False)
            cls._CONFIG.read(config_file)
        else:
            getLogger(__name__).warning('Log config file "%s" does not exist. '
                                        'Using default Python configuration.',
                                        config_file)

    @classmethod
    def add_stream_handler(cls, stream):
        """Output all logs to the given stream.

        Args:
            stream: Object that supports ``write()`` and ``flush()``.
        """
        handler = StreamHandler(stream)
        cls._add_handler(handler)
        return handler

    @classmethod
    def _add_handler(cls, handler):
        """Add handler to loggers.

        Use formatter_console if exists.

        Args:
            handler(Handler): Handle to be added.
        """
        if cls._CONFIG.has_section(cls._DEFAULT_FMT):
            fmt_conf = cls._CONFIG[cls._DEFAULT_FMT]
            fmt = Formatter(fmt_conf.get('format', None),
                            fmt_conf.get('datefmt', None))
            handler.setFormatter(fmt)
        getLogger().addHandler(handler)


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
        logger = getLogger(napp_id)
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
