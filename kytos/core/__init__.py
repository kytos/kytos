"""Kytos.core is the module with main classes used in Kytos."""
import sys

from kytos.core.auth import authenticated
from kytos.core.controller import Controller
from kytos.core.events import KytosEvent
from kytos.core.logs import get_napp_logger
from kytos.core.napps import KytosNApp, rest

from .metadata import __version__

__all__ = (
    "authenticated",
    "Controller",
    "KytosEvent",
    "KytosNApp",
    "log",
    "rest",
    "__version__",
)

# Kept lowercase to be more user friendly.
log = property(lambda self: self.get_napp_logger()) \
              .__get__(sys.modules[__name__])
