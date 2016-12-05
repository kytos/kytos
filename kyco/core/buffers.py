"""Kyco Buffer Classes, based on Python Queue."""
import logging
from queue import Queue

from kyco.core.events import KycoEvent

__all__ = ('KycoBuffers')

log = logging.getLogger(__name__)


class KycoEventBuffer(object):
    """KycoEventBuffer represents a queue to store a set of KycoEvents."""

    def __init__(self, name, event_base_class=None):
        """Contructor of KycoEventBuffer receive the parameters below.

        Parameters:
            name (string): name of KycoEventBuffer.
            event_base_class (class): Class of KycoEvent.
        """
        self.name = name
        self._queue = Queue()
        self._event_base_class = event_base_class
        self._reject_new_events = False

    def put(self, event):
        """Insert a event in KycoEventBuffer if reject new events is False.

        Reject new events is True when a kyco/core.shutdown message was
        received.
        """
        if not self._reject_new_events:
            self._queue.put(event)
            log.debug('[buffer: %s] Added: %s', self.name, event.name)

        if event.name == "kyco/core.shutdown":
            log.info('[buffer: %s] Stop mode enabled. Rejecting new events.',
                     self.name)
            self._reject_new_events = True

    def get(self):
        """Remove and return a event from top of queue."""
        event = self._queue.get()

        log.debug('[buffer: %s] Removed: %s', self.name, event.name)

        return event

    def task_done(self):
        """Indicate that a formerly enqueued task is complete.

        If a :func:`~kyco.core.KycoEventBuffer.join` is currently blocking,
        it will resume if all itens in KycoEventBuffer have been processed
        (meaning that a task_done() call was received for every item that had
        been put() into the KycoEventBuffer).
        """
        self._queue.task_done()

    def join(self):
        """Block until all events are gotten and processed.

        A item is processed when the method task_done is called.
        """
        self._queue.join()

    def qsize(self):
        """Return the size of KycoEventBuffer."""
        return self._queue.qsize()

    def empty(self):
        """Return True if KycoEventBuffer is empty."""
        return self._queue.empty()

    def full(self):
        """Return True if KycoEventBuffer is full of KycoEvent."""
        return self._queue.full()


class KycoBuffers(object):
    """KycoBuffers represents a set of KycoEventBuffer used in Kyco."""

    def __init__(self):
        """Constructor of KycoBuffer build four KycoEventBuffers.

        RawEvent:   KycoEventBuffer with events received from network.
        MsgInEvent: KycoEventBuffer with events to be received.
        MsgOutEvent: KycoEventBuffer with events to be sent.
        AppEvent: KycoEventBuffer with events sent to NApps.
        """
        self.raw = KycoEventBuffer('raw_event')
        self.msg_in = KycoEventBuffer('msg_in_event')
        self.msg_out = KycoEventBuffer('msg_out_event')
        self.app = KycoEventBuffer('app_event')

    def send_stop_signal(self):
        """Method usd to send a kyco/core.shutdown event to all buffers."""
        log.info('Stop signal received by Kyco buffers.')
        log.info('Sending KycoShutdownEvent to all apps.')
        event = KycoEvent(name='kyco/core.shutdown')
        self.raw.put(event)
        self.msg_in.put(event)
        self.msg_out.put(event)
        self.app.put(event)
