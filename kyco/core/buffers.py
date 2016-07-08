"""Kyco Buffer Classes, based on Python Queue"""
import logging
from queue import Queue
from threading import Event as Semaphore

from kyco.core.events import KycoRawEvent
from kyco.core.events import KycoMsgEvent
from kyco.core.events import KycoAppEvent

__all__ = ['KycoBuffers']

log = logging.getLogger('Kyco')


class KycoEventBuffer(object):
    """Class that """
    def __init__(self, name, event_base_class):
        self.name = name
        self._queue = Queue()
        self._semaphore = Semaphore()
        self._event_base_class = event_base_class

    def put(self, new_event):
        if not isinstance(new_event, self._event_base_class):
            # TODO: Specific exception
            raise Exception("This event can not be added to this buffer")
        log.debug('Added new event to %s event buffer', self.name)
        self._queue.put(new_event)
        self._semaphore.set()

    def get(self):
        self._semaphore.wait()
        log.debug('Removing event from %s event buffer', self.name)
        event = self._queue.get()
        if self._queue.empty():
            self._semaphore.clear()
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
        self.raw_events = KycoEventBuffer('raw_event', KycoRawEvent)
        self.msg_in_events = KycoEventBuffer('msg_in_event', KycoMsgEvent)
        self.msg_out_events = KycoEventBuffer('msg_out_event', KycoMsgEvent)
        self.app_events = KycoEventBuffer('app_event', KycoAppEvent)
