"""Kytos.core is the module with main classes used in Kytos."""
from kytos.core.controller import Controller
from kytos.core.events import KytosEvent
from kytos.core.logs import NAppLog
from kytos.core.napps import KytosNApp, rest

from .metadata import __version__

__all__ = ('Controller', 'KytosEvent', 'KytosNApp', 'log', 'rest',
           '__version__')

# Kept lowercase to be more user friendly.
log = NAppLog()  # pylint: disable=invalid-name
