"""Kytos Buffer Classes, based on Python Queue."""
import logging
from queue import Queue

from kytos.core.events import KytosEvent

__all__ = ('KytosBuffers', )

log = logging.getLogger(__name__)


class KytosEventBuffer(object):
    """KytosEventBuffer represents a queue to store a set of KytosEvents."""

    def __init__(self, name, event_base_class=None):
        """Contructor of KytosEventBuffer receive the parameters below.

        Parameters:
            name (string): name of KytosEventBuffer.
            event_base_class (class): Class of KytosEvent.
        """
        self.name = name
        self._queue = Queue()
        self._event_base_class = event_base_class
        self._reject_new_events = False

    def put(self, event):
        """Insert a event in KytosEventBuffer if reject new events is False.

        Reject new events is True when a kytos/core.shutdown message was
        received.
        """
        if not self._reject_new_events:
            self._queue.put(event)
            log.debug('[buffer: %s] Added: %s', self.name, event.name)

        if event.name == "kytos/core.shutdown":
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

        If a :func:`~kytos.core.KytosEventBuffer.join` is currently blocking,
        it will resume if all itens in KytosEventBuffer have been processed
        (meaning that a task_done() call was received for every item that had
        been put() into the KytosEventBuffer).
        """
        self._queue.task_done()

    def join(self):
        """Block until all events are gotten and processed.

        A item is processed when the method task_done is called.
        """
        self._queue.join()

    def qsize(self):
        """Return the size of KytosEventBuffer."""
        return self._queue.qsize()

    def empty(self):
        """Return True if KytosEventBuffer is empty."""
        return self._queue.empty()

    def full(self):
        """Return True if KytosEventBuffer is full of KytosEvent."""
        return self._queue.full()


class KytosBuffers(object):
    """KytosBuffers represents a set of KytosEventBuffer used in Kytos."""

    def __init__(self):
        """Constructor of KytosBuffer build four KytosEventBuffers.

        RawEvent:   KytosEventBuffer with events received from network.
        MsgInEvent: KytosEventBuffer with events to be received.
        MsgOutEvent: KytosEventBuffer with events to be sent.
        AppEvent: KytosEventBuffer with events sent to NApps.
        """
        self.raw = KytosEventBuffer('raw_event')
        self.msg_in = KytosEventBuffer('msg_in_event')
        self.msg_out = KytosEventBuffer('msg_out_event')
        self.app = KytosEventBuffer('app_event')

    def send_stop_signal(self):
        """Method usd to send a kytos/core.shutdown event to all buffers."""
        log.info('Stop signal received by Kytos buffers.')
        log.info('Sending KytosShutdownEvent to all apps.')
        event = KytosEvent(name='kytos/core.shutdown')
        self.raw.put(event)
        self.msg_in.put(event)
        self.msg_out.put(event)
        self.app.put(event)
