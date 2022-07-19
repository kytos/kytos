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


def extend_descriptors(inst, **kwargs):
    """Creates wrapper of instance with descriptors"""

    class MFacade:
        """Wrapper class for provided instance"""

        def __getattr__(self, name):
            return getattr(inst, name)

    for (key, value) in kwargs.items():
        setattr(MFacade, key, value)
    return MFacade()


@property
def log(self):
    """Get appropriate napp logger at module import time,
    rather than module initialization time"""
    return self.get_napp_logger()


sys.modules[__name__] = extend_descriptors(sys.modules[__name__], log=log)
