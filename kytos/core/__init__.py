"""Kytos.core is the module with main classes used in Kytos."""
from kytos.core.controller import Controller
from kytos.core.logs import NAppLog
from .metadata import __version__

__all__ = 'Controller', 'log', '__version__'

log = NAppLog()
