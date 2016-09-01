"""Kyco Buffer Classes, based on Python Queue"""
import logging
from queue import Queue

from kyco.core.events import (KycoAppEvent, KycoMsgEvent, KycoRawEvent,
                              KycoShutdownEvent)

__all__ = ['KycoBuffers']

log = logging.getLogger('Kyco')


class KycoEventBuffer(object):
    """Class that """
    def __init__(self, name, event_base_class):
        self.name = name
        self._queue = Queue()
        self._event_base_class = event_base_class
        self._reject_new_events = False

    def put(self, event):
        if not self._reject_new_events:
            if not isinstance(event, self._event_base_class) and \
                    not isinstance(event, KycoShutdownEvent):
                # TODO: Raise a more proper exception
                msg = "{} event can not be added to {} buffer"
                raise Exception(msg.format(type(event).__name__, self.name))

            self._queue.put(event)
            log.debug('[buffer: %s] Added: %s', self.name,
                      type(event).__name__)

        if isinstance(event, KycoShutdownEvent):
            log.info('[buffer: %s] Stop mode enabled. Rejecting new events.',
                     self.name)
            self._reject_new_events = True

    def get(self):
        event = self._queue.get()

        log.debug('[buffer: %s] Removed: %s', self.name,
                  type(event).__name__)

        return event

    def task_done(self):
        self._queue.task_done()

    def join(self):
        self._queue.join()

    def qsize(self):
        return self._queue.qsize()

    def empty(self):
        return self._queue.empty()

    def full(self):
        return self._queue.full()


class KycoBuffers(object):
    def __init__(self):
        self.raw = KycoEventBuffer('raw_event', KycoRawEvent)
        self.msg_in = KycoEventBuffer('msg_in_event', KycoMsgEvent)
        self.msg_out = KycoEventBuffer('msg_out_event', KycoMsgEvent)
        self.app = KycoEventBuffer('app_event', KycoAppEvent)

    def send_stop_signal(self):
        log.info('Stop signal received by Kyco buffers.')
        log.info('Sending KycoShutdownEvent to all apps.')
        event = KycoShutdownEvent()
        self.raw.put(event)
        self.msg_in.put(event)
        self.msg_out.put(event)
        self.app.put(event)
