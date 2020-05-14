"""Module responsible for running and managing NApps."""
from kytos.core.api_server import APIServer

from .base import KytosNApp, NApp
from .manager import NAppsManager  # pylint: disable=cyclic-import

__all__ = ('NApp', 'KytosNApp', 'NAppsManager', 'rest')

# Decorator should be lowercase
rest = APIServer.decorate_as_endpoint  # pylint: disable=invalid-name
