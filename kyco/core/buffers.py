"""Kyco Buffer Classes, based on Python Queue"""
import logging
from queue import Queue
from threading import Event as Semaphore

__all__ = ['KycoBuffers']

log = logging.getLogger('Kyco')


class KycoEventBuffer(object):
    def __init__(self, name):
        self.name = name
        self._queue = Queue()
        self._semaphore = Semaphore()

    def put(self, new_event):
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
        self.raw_events = KycoEventBuffer('raw_event')
        self.msg_in_events = KycoEventBuffer('msg_in_event')
        self.msg_out_events = KycoEventBuffer('msg_out_event')
        self.app_events = KycoEventBuffer('app_event')
