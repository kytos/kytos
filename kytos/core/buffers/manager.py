"""Kytos Buffer Classes, based on Python Queue."""
import logging

from janus import PriorityQueue, Queue

from kytos.core.config import KytosConfig
from kytos.core.events import KytosEvent
from kytos.core.helpers import get_thread_pool_max_workers

from .buffers import KytosEventBuffer
from .factory import buffer_from_config

LOG = logging.getLogger(__name__)


class KytosBuffers:
    """Set of KytosEventBuffer used in Kytos."""

    def __init__(self):
        """Build four KytosEventBuffers.

        :attr:`conn`: :class:`~kytos.core.buffers.KytosEventBuffer` with events
        received from connection events.

        :attr:`raw`: :class:`~kytos.core.buffers.KytosEventBuffer` with events
        received from network.

        :attr:`msg_in`: :class:`~kytos.core.buffers.KytosEventBuffer` with
        events to be received.

        :attr:`msg_out`: :class:`~kytos.core.buffers.KytosEventBuffer` with
        events to be sent.

        :attr:`app`: :class:`~kytos.core.buffers.KytosEventBuffer` with events
        sent to NApps.
        """

        self._pool_max_workers = get_thread_pool_max_workers()

        self.conn = KytosEventBuffer("conn")
        self.raw = KytosEventBuffer(
            "raw",
            queue=Queue(maxsize=self._get_maxsize("sb"))
        )
        self.msg_in = KytosEventBuffer(
            "msg_in",
            queue=PriorityQueue(maxsize=self._get_maxsize("sb")),
        )
        self.msg_out = KytosEventBuffer(
            "msg_out",
            queue=PriorityQueue(maxsize=self._get_maxsize("sb")),
        )
        self.app = KytosEventBuffer(
            "app",
            queue=Queue(maxsize=self._get_maxsize("app")),
        )

        buffer_conf = KytosConfig().options['daemon'].event_buffer_conf

        for name, config in buffer_conf.items():
            setattr(self, name, buffer_from_config(name, config))

    def get_all_buffers(self):
        """Get all KytosEventBuffer instances."""
        return [
            event_buffer for event_buffer in self.__dict__.values()
            if isinstance(event_buffer, KytosEventBuffer)
        ]

    def _get_maxsize(self, queue_name):
        """Get queue maxsize if it's been set."""
        return self._pool_max_workers.get(queue_name, 0)

    def send_stop_signal(self):
        """Send a ``kytos/core.shutdown`` event to each buffer."""
        LOG.info('Stop signal received by Kytos buffers.')
        LOG.info('Sending KytosShutdownEvent to all apps.')
        event = KytosEvent(name='kytos/core.shutdown')
        for buffer in self.get_all_buffers():
            buffer.put(event)
