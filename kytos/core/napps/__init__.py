"""Module responsible for running and managing NApps."""
from .base import KytosNApp, NApp
from .manager import NAppsManager
# pylint does not recognize the import below as local
from kytos.core.api_server import APIServer  # pylint: disable=C0411

__all__ = ('NApp', 'KytosNApp', 'NAppsManager', 'rest')

# Decorator should be lowercase
rest = APIServer.decorate_as_endpoint  # pylint: disable=invalid-name
