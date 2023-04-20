"""Module with utilities to create tests."""
from unittest.mock import MagicMock, create_autospec

from httpx import AsyncClient

from kytos.core import Controller
from kytos.core.auth import Auth
from kytos.core.config import KytosConfig
from kytos.core.connection import (Connection, ConnectionProtocol,
                                   ConnectionState)
from kytos.core.events import KytosEvent
from kytos.core.interface import Interface
from kytos.core.link import Link
from kytos.core.switch import Switch


def get_controller_mock():
    """Return a controller mock."""
    options = KytosConfig().options['daemon']
    Auth.get_user_controller = MagicMock()
    controller = Controller(options)
    controller.log = MagicMock()
    return controller


def get_interface_mock(name, port_number, switch, address="00:00:00:00:00:00"):
    """Return a interface mock."""
    interface = create_autospec(Interface)
    interface.id = f"{switch.dpid}:{port_number}"
    interface.name = name
    interface.port_number = port_number
    interface.switch = switch
    interface.address = address
    interface.lldp = True
    return interface


def get_link_mock(endpoint_a, endpoint_b):
    """Return a link mock."""
    link = create_autospec(Link)
    link.endpoint_a = endpoint_a
    link.endpoint_b = endpoint_b
    link.metadata = {"A": 0, "BB": 0.0, "CCC": "test"}
    return link


def get_switch_mock(dpid, of_version=None):
    """Return a switch mock."""
    switch = create_autospec(Switch)
    switch.dpid = dpid
    if of_version:
        switch.ofp_version = '0x0' + str(of_version)
        switch.connection = get_connection_mock(of_version, switch)
    return switch


def get_connection_mock(of_version, switch, address="00:00:00:00:00:00",
                        state=ConnectionState.NEW):
    """Return a connection mock."""
    protocol = create_autospec(ConnectionProtocol)
    protocol.version = of_version
    connection = create_autospec(Connection)
    connection.protocol = protocol
    connection.switch = switch
    connection.address = address
    connection.state = state
    return connection


def get_kytos_event_mock(name, content):
    """Return a kytos event mock."""
    event = create_autospec(KytosEvent)
    event.name = name
    event.content = content
    event.message = content.get('message')
    event.destination = content.get('destination')
    event.source = content.get('source')
    return event


def get_test_client(controller, napp) -> AsyncClient:
    """Return an async api test client."""
    controller.api_server.register_napp_endpoints(napp)
    app = controller.api_server.app
    base_url = "http://127.0.0.1/api/"
    return AsyncClient(app=app, base_url=base_url)
