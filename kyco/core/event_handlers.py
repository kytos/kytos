"""Handlers of KycoBuffers"""
import logging
import re

from threading import Thread

from kyco.core.events import KycoNullEvent
from kyco.core.events import KycoRawEvent
from kyco.core.events import KycoRawOpenFlowMessage
from kyco.core.events import KycoRawConnectionUp
from kyco.core.events import KycoRawConnectionDown
from kyco.core.exceptions import KycoWrongEventType

log = logging.getLogger('Kyco')


def raw_event_handler(listeners,
                      connection_pool,
                      raw_buffer,
                      msg_in_buffer,
                      app_buffer):
    log.info("Raw Event Handler started")
    while True:
        event = raw_buffer.get()
        if isinstance(event, KycoNullEvent):
            log.debug("RawEvent handler stopped")
            break
        log.debug("RawEvent handler called")

        if not issubclass(type(event), KycoRawEvent):
            message = 'RawEventHandler expects a KycoRawEvent.'
            raise KycoWrongEventType(message, event)

        if isinstance(event, KycoRawConnectionUp):
            connection_id = event.content.get('connection')
            connection_request = event.content.get('request')
            connection_pool[connection_id] = connection_request

        if isinstance(event, KycoRawConnectionDown):
            connection_id = event.content.get('connection')
            connection_pool.pop(connection_id)

        for key in listeners:
            if re.match(key, type(event).__name__):
                for listener in listeners[key]:
                    Thread(target=listener, args=[event]).start()


def msg_in_event_handler(listeners, msg_in_buffer):
    log.info("Message In Event Handler started")
    while True:
        event = msg_in_buffer.get()
        if isinstance(event, KycoNullEvent):
            log.debug("MsgInEvent handler stopped")
            break
        log.debug("MsgInEvent handler called")

        for key in listeners:
            if re.match(key, type(event).__name__):
                for listener in listeners[key]:
                    Thread(target=listener, args=[event]).start()


def msg_out_event_handler(listeners, connection_pool, msg_out_buffer):
    log.info("Message Out Event Handler started")
    while True:
        event = msg_out_buffer.get()
        if isinstance(event, KycoNullEvent):
            log.debug("MsgOutEvent handler stopped")
            break
        log.debug("MsgOutEvent handler called")

        send_to_switch(connection_pool[event.content.get('connection')],
                       event.content.get('message').pack())

        for key in listeners:
            if re.match(key, type(event).__name__):
                for listener in listeners[key]:
                    Thread(target=listener, args=[event]).start()


def app_event_handler(listeners, app_buffer):
    log.info("App Event Handler started")
    while True:
        event = app_buffer.get()
        if isinstance(event, KycoNullEvent):
            log.debug("AppEvent handler stopped")
            break
        log.debug("AppEvent handler called\n")


def send_to_switch(connection, message):
    """
     Args:
        connection (socket/request): socket connection to switch
        message (binary OpenFlowMessage)
    """
    connection.send(message)
