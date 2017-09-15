"""Module responsible for running and managing NApps."""
from .base import NApp, KytosNApp
from .manager import NAppsManager
from kytos.core.api_server import APIServer

__all__ = 'NApp', 'KytosNApp', 'NAppsManager', 'rest'

rest = APIServer.decorate_as_endpoint
