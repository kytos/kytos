"""Handlers of KycoBuffers"""
import logging
import re

from threading import Thread

from kyco.core.events import KycoShutdownEvent
from kyco.core.events import KycoRawEvent
from kyco.core.events import KycoRawOpenFlowMessage
from kyco.core.events import KycoRawConnectionUp
from kyco.core.events import KycoRawConnectionDown
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

        if not issubclass(type(event), KycoRawEvent):
            message = 'RawEventHandler expects a KycoRawEvent.'
            raise KycoWrongEventType(message, event)

        # TODO: This should not be here
        if isinstance(event, KycoRawConnectionUp):
            connection_request = event.content['request']
            connection_pool[event.connection] = connection_request

        # TODO: This should not be here
        if isinstance(event, KycoRawConnectionDown):
            connection_pool.pop(event.connection)

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


# TODO: Create a Switch class and a method send()
def send_to_switch(connection, message):
    """
     Args:
        connection (socket/request): socket connection to switch
        message (binary OpenFlowMessage)
    """
    connection.send(message)
