"""Handlers of KycoBuffers"""
import logging
import re

from threading import Thread

from kyco.core.events import KycoShutdownEvent
from kyco.core.events import KycoSwitchDown
from kyco.core.events import KycoSwitchUp
from kyco.core.events import KycoNewConnection
from kyco.core.events import KycoConnectionLost
from kyco.core.exceptions import KycoWrongEventType

log = logging.getLogger('Kyco')


def notify_listeners(listeners, event):
    for key in listeners:
        if re.match(key, type(event).__name__):
            for listener in listeners[key]:
                Thread(target=listener, args=[event]).start()


def raw_event_handler(listeners, connection_pool, raw_buffer, msg_in_buffer,
                      app_buffer):
    log.info("Raw Event Handler started")
    while True:
        event = raw_buffer.get()
        log.debug("RawEvent handler called")

        if isinstance(event, KycoShutdownEvent):
            log.debug("RawEvent handler stopped")
            break

        notify_listeners(listeners, event)


def msg_in_event_handler(listeners, msg_in_buffer):
    log.info("Message In Event Handler started")
    while True:
        event = msg_in_buffer.get()
        log.debug("MsgInEvent handler called")

        if isinstance(event, KycoShutdownEvent):
            log.debug("MsgInEvent handler stopped")
            break

        notify_listeners(listeners, event)


def msg_out_event_handler(listeners, connection_pool, msg_out_buffer):
    log.info("Message Out Event Handler started")
    while True:
        event = msg_out_buffer.get()
        log.debug("MsgOutEvent handler called")
        if isinstance(event, KycoShutdownEvent):
            log.debug("MsgOutEvent handler stopped")
            break

        message = event.content['message']

        send_to_switch(connection_pool[event.connection], message.pack())
        notify_listeners(listeners, event)


def app_event_handler(listeners, app_buffer):
    log.info("App Event Handler started")
    while True:
        event = app_buffer.get()
        log.debug("AppEvent handler called")
        if isinstance(event, KycoShutdownEvent):
            log.debug("AppEvent handler stopped")
            break

        notify_listeners(listeners, event)


def new_connection_handler(connection_pool, add_to_app_buffer, event):
    """Handle a NewConnection event.

    This method will read the event and store the connection (socket) data into
    the correct switch object on the controller.

    At last, it will create and send a SwitchUp event to the app buffer.

    Args:
        connection_pool (list): For now here is where we store sockets.
        app_buffer (KycoBuffer): The buffer that will receive the new event.
        event (KycoNewConnection): The received event with the needed infos.
    """

    log.info("Handling KycoNewConnection event")

    # Saving the socket reference
    connection_request = event.content['request']
    connection_pool[event.connection] = connection_request

    new_event = KycoSwitchUp(content={}, connection=event.connection,
                             timestamp=event.timestamp)

    add_to_app_buffer(new_event)


def connection_lost_handler(connection_pool, add_to_app_buffer, event):
    """Handle a ConnectionLost event.

    This method will read the event and change the switch that has been
    disconnected.

    At last, it will create and send a SwitchDown event to the app buffer.

    Args:
        connection_pool (list): For now here is where we store sockets.
        app_buffer (KycoBuffer): The buffer that will receive the new event.
        event (KycoConnectionLost): Received event with the needed infos.
    """

    log.info("Handling KycoConnectionLost event")

    # For now we just remove the connection from the connection_pool dict
    connection_pool.pop(event.connection)

    new_event = KycoSwitchDown(content={}, connection=event.connection,
                               timestamp=event.timestamp)

    add_to_app_buffer(new_event)


# TODO: Create a Switch class and a method send()
def send_to_switch(connection, message):
    """ Send a message to through the given connection

    Args:
        connection (socket/request): socket connection to switch
        message (binary OpenFlowMessage)

    """
    connection.send(message)
