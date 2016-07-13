"""Handlers of KycoBuffers"""
import logging

from struct import unpack
from kyco.core.events import KycoRawOpenFlowMessageIn
log = logging.getLogger('Kyco')


def raw_event_handler(listeners, raw_buffer, msg_in_buffer, app_buffer):
    log.info("Raw Event Handler started")
    while True:
        event = raw_buffer.get()
        log.debug("\n#######################################################\n"
                  "                 RawEvent handler called\n"
                  "#######################################################\n")
        log.debug('KycoRawEvent read...')
        # log.debug("%s: %s", event.context, event.content)
        if isinstance(event, KycoRawOpenFlowMessageIn):
            for listener in listeners['KycoRawOpenFlowMessageIn']:
                listener(event)

        # data = unpack('!B', data)[0]
        # addr = writer.get_extra_info('peername')
        # log.debug("[Message Handler] New OF Message '%s' received from %s",
        # str(data), addr)
        # message = (addr, data)
        # msg_in_buffer.put(message)


def msg_in_event_handler(listeners, msg_in_buffer):
    log.info("Message In Event Handler started")
    # msg = "[Message Processor] MessageInEvenet %s"
    while True:
        event = msg_in_buffer.get()
        log.debug("\n#######################################################\n"
                  "                 MsgInEvent handler called\n"
                  "#######################################################\n")
        log.debug("%s: %s", event.context, event.content)
        # apps = self._events_listeners[0]
        # executor = ThreadPoolExecutor(max_workers=len(apps))
        # self.executors.append(executor)
        # [executor.submit(app.handle_event, message_event) for app in apps]


def msg_out_event_handler(listeners, msg_out_buffer):
    log.info("Message Out Event Handler started")
    # msg = "[Message Processor] MessageInEvenet %s"
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
    # msg = "[Message Processor] MessageInEvenet %s"
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
