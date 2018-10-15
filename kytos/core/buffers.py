"""Kytos Buffer Classes, based on Python Queue."""
import logging

# from queue import Queue
from janus import Queue

from kytos.core.events import KytosEvent

__all__ = ('KytosBuffers', )

LOG = logging.getLogger(__name__)


class KytosEventBuffer:
    """KytosEventBuffer represents a queue to store a set of KytosEvents."""

    def __init__(self, name, event_base_class=None, loop=None):
        """Contructor of KytosEventBuffer receive the parameters below.

        Args:
            name (string): name of KytosEventBuffer.
            event_base_class (class): Class of KytosEvent.
        """
        self.name = name
        self._event_base_class = event_base_class
        self._loop = loop
        self._queue = Queue(loop=self._loop)
        self._reject_new_events = False

    def put(self, event):
        """Insert an event in KytosEventBuffer if reject_new_events is False.

        Reject new events is True when a kytos/core.shutdown message was
        received.

        Args:
            event (:class:`~kytos.core.events.KytosEvent`):
                KytosEvent sent to queue.
        """
        if not self._reject_new_events:
            self._queue.sync_q.put(event)
            LOG.debug('[buffer: %s] Added: %s', self.name, event.name)

        if event.name == "kytos/core.shutdown":
            LOG.info('[buffer: %s] Stop mode enabled. Rejecting new events.',
                     self.name)
            self._reject_new_events = True

    async def aput(self, event):
        """Insert a event in KytosEventBuffer if reject new events is False.

        Reject new events is True when a kytos/core.shutdown message was
        received.

        Args:
            event (:class:`~kytos.core.events.KytosEvent`):
                KytosEvent sent to queue.
        """
        # qsize = self._queue.async_q.qsize()
        # print('qsize before:', qsize)
        if not self._reject_new_events:
            await self._queue.async_q.put(event)
            LOG.debug('[buffer: %s] Added: %s', self.name, event.name)

        # qsize = self._queue.async_q.qsize()
        # print('qsize after:', qsize)

        if event.name == "kytos/core.shutdown":
            LOG.info('[buffer: %s] Stop mode enabled. Rejecting new events.',
                     self.name)
            self._reject_new_events = True

    def get(self):
        """Remove and return a event from top of queue.

        Returns:
            :class:`~kytos.core.events.KytosEvent`:
                Event removed from top of queue.

        """
        event = self._queue.sync_q.get()

        LOG.debug('[buffer: %s] Removed: %s', self.name, event.name)

        return event

    async def aget(self):
        """Remove and return a event from top of queue.

        Returns:
            :class:`~kytos.core.events.KytosEvent`:
                Event removed from top of queue.

        """
        event = await self._queue.async_q.get()

        LOG.debug('[buffer: %s] Removed: %s', self.name, event.name)

        return event

    def task_done(self):
        """Indicate that a formerly enqueued task is complete.

        If a :func:`~kytos.core.buffers.KytosEventBuffer.join` is currently
        blocking, it will resume if all itens in KytosEventBuffer have been
        processed (meaning that a task_done() call was received for every item
        that had been put() into the KytosEventBuffer).
        """
        self._queue.sync_q.task_done()

    def join(self):
        """Block until all events are gotten and processed.

        A item is processed when the method task_done is called.
        """
        self._queue.sync_q.join()

    def qsize(self):
        """Return the size of KytosEventBuffer."""
        return self._queue.sync_q.qsize()

    def empty(self):
        """Return True if KytosEventBuffer is empty."""
        return self._queue.sync_q.empty()

    def full(self):
        """Return True if KytosEventBuffer is full of KytosEvent."""
        return self._queue.sync_q.full()


class KytosBuffers:
    """Set of KytosEventBuffer used in Kytos."""

    def __init__(self, loop=None):
        """Build four KytosEventBuffers.

        :attr:`raw`: :class:`~kytos.core.buffers.KytosEventBuffer` with events
        received from network.

        :attr:`msg_in`: :class:`~kytos.core.buffers.KytosEventBuffer` with
        events to be received.

        :attr:`msg_out`: :class:`~kytos.core.buffers.KytosEventBuffer` with
        events to be sent.

        :attr:`app`: :class:`~kytos.core.buffers.KytosEventBuffer` with events
        sent to NApps.
        """
        self._loop = loop
        self.raw = KytosEventBuffer('raw_event', loop=self._loop)
        self.msg_in = KytosEventBuffer('msg_in_event', loop=self._loop)
        self.msg_out = KytosEventBuffer('msg_out_event', loop=self._loop)
        self.app = KytosEventBuffer('app_event', loop=self._loop)

    def send_stop_signal(self):
        """Send a ``kytos/core.shutdown`` event to each buffer."""
        LOG.info('Stop signal received by Kytos buffers.')
        LOG.info('Sending KytosShutdownEvent to all apps.')
        event = KytosEvent(name='kytos/core.shutdown')
        self.raw.put(event)
        self.msg_in.put(event)
        self.msg_out.put(event)
        self.app.put(event)
