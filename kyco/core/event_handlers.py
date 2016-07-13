"""Handlers of KycoBuffers"""
import logging
import re

from struct import unpack
from threading import Thread

from kyco.core.events import KycoRawOpenFlowMessageIn
from kyco.core.events import KycoRawConnectionUp
log = logging.getLogger('Kyco')


def raw_event_handler(listeners,
                      connection_pool,
                      raw_buffer,
                      msg_in_buffer,
                      app_buffer):
    log.info("Raw Event Handler started")
    while True:
        event = raw_buffer.get()
        log.debug("\n#######################################################\n"
                  "                 RawEvent handler called\n"
                  "#######################################################\n")
        log.debug('KycoRawEvent read...')

        if type(event) is KycoRawConnectionUp:
            connection_id = event.content.get('connection')
            connection_request = event.content.get('request')
            connection_pool[connection_id] = connection_request

        # log.debug("%s: %s", event.context, event.content)
        if isinstance(event, KycoRawOpenFlowMessageIn):
            for listener in listeners['KycoRawOpenFlowMessageIn']:
                Thread(target=listener, args=[event]).start()


def msg_in_event_handler(listeners, msg_in_buffer):
    log.info("Message In Event Handler started")
    while True:
        event = msg_in_buffer.get()
        log.debug("\n#######################################################\n"
                  "                 MsgInEvent handler called\n"
                  "#######################################################\n")
        log.debug("%s: %s", event.context, event.content)

        for key in listeners:
            if re.match(key, type(event).__name__):
                for listener in listeners[key]:
                    Thread(target=listener, args=[event]).start()

def msg_out_event_handler(listeners, msg_out_buffer):
    log.info("Message Out Event Handler started")
    while True:
        event = msg_out_buffer.get()
        log.debug("\n#######################################################\n"
                  "                 MsgOutEvent handler called\n"
                  "#######################################################\n")
        log.debug("%s: %s", event.context, event.content)

        # apps = self._events_listeners[0]
        # executor = ThreadPoolExecutor(max_workers=len(apps))
        # self.executors.append(executor)
        # [executor.submit(app.handle_event, message_event) for app in apps]


def app_event_handler(listeners, app_buffer):
    log.info("App Event Handler started")
    while True:
        event = app_buffer.get()
        log.debug("\n#######################################################\n"
                  "                 AppEvent handler called\n"
                  "#######################################################\n")
        log.debug("%s: %s", event.context, event.content)
        # apps = self._events_listeners[0]
        # executor = ThreadPoolExecutor(max_workers=len(apps))
        # self.executors.append(executor)
        # [executor.submit(app.handle_event, message_event) for app in apps]
