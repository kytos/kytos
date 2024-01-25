"""Test kytos.core.buffers module."""
import asyncio
from unittest.mock import MagicMock

import pytest
from janus import Queue

from kytos.core.buffers import KytosBuffers, KytosEventBuffer
from kytos.core.events import KytosEvent


@pytest.mark.parametrize("queue_name", ["msg_out", "msg_in"])
async def test_priority_queues(queue_name):
    """Test KytosBuffers priority queues."""
    buffers = KytosBuffers()

    prios = [-10, 10, 0, -20]
    for prio in prios:
        queue = getattr(buffers, queue_name)
        await queue.aput(KytosEvent(priority=prio))
    for prio in sorted(prios):
        event = await queue.aget()
        assert event.priority == prio


# pylint: disable=protected-access
class TestKytosEventBuffer:
    """KytosEventBuffer tests."""

    @staticmethod
    def create_event_mock(name='any'):
        """Create a new event mock."""
        event = MagicMock()
        event.name = name
        return event

    async def test_put_get(self):
        """Test put and get methods."""
        kytos_event_buffer = KytosEventBuffer('name')
        event = self.create_event_mock()

        kytos_event_buffer.put(event)
        queue_event = kytos_event_buffer.get()
        assert queue_event == event

        kytos_event_buffer._queue.close()
        await kytos_event_buffer._queue.wait_closed()

    async def test_put__shutdown(self):
        """Test put method to shutdown event."""
        kytos_event_buffer = KytosEventBuffer("name")
        assert not kytos_event_buffer._reject_new_events
        event = KytosEvent("kytos/core.shutdown")
        kytos_event_buffer.put(event)

        assert kytos_event_buffer._reject_new_events
        kytos_event_buffer._queue.close()
        await kytos_event_buffer._queue.wait_closed()

    async def test_aput(self):
        """Test aput async method."""
        event = KytosEvent("kytos/core.shutdown")
        kytos_event_buffer = KytosEventBuffer("name")
        await kytos_event_buffer.aput(event)
        assert kytos_event_buffer._reject_new_events

    async def test_aput_aget(self):
        """Test aput async method."""
        event = KytosEvent('some_event')
        kytos_event_buffer = KytosEventBuffer("name")
        await kytos_event_buffer.aput(event)
        got_event = await kytos_event_buffer.aget()
        assert got_event == event

    async def test_task_done(self, monkeypatch):
        """Test task_done method."""
        mock_task_done = MagicMock()
        monkeypatch.setattr("janus._SyncQueueProxy.task_done", mock_task_done)
        kytos_event_buffer = KytosEventBuffer("name")
        kytos_event_buffer.task_done()
        mock_task_done.assert_called()

    async def test_join(self, monkeypatch):
        """Test join method."""
        mock = MagicMock()
        monkeypatch.setattr("janus._SyncQueueProxy.join", mock)
        kytos_event_buffer = KytosEventBuffer("name")
        kytos_event_buffer.join()
        mock.assert_called()

    async def test_qsize(self):
        """Test qsize method to empty and with one event in query."""
        kytos_event_buffer = KytosEventBuffer("name")
        assert kytos_event_buffer.qsize() == 0
        await kytos_event_buffer.aput(KytosEvent("some_event"))
        assert kytos_event_buffer.qsize() == 1

    async def test_empty(self):
        """Test empty method to empty and with one event in query."""
        kytos_event_buffer = KytosEventBuffer("name")
        assert kytos_event_buffer.empty()
        await kytos_event_buffer.aput(KytosEvent("some_event"))
        assert not kytos_event_buffer.empty()

    async def test_full(self):
        """Test full method to full."""
        kytos_event_buffer = KytosEventBuffer("name", queue=Queue(maxsize=1))
        assert not kytos_event_buffer.full()
        assert kytos_event_buffer.empty()

        event = KytosEvent("some_event")
        await kytos_event_buffer.aput(event)
        assert kytos_event_buffer.full()
        assert not kytos_event_buffer.empty()
        await kytos_event_buffer.aget()


class TestKytosBuffers:
    """KytosBuffers tests."""

    async def test_send_stop_signal(self):
        """Test send_stop_signal method."""
        kytos_buffers = KytosBuffers()
        kytos_buffers.send_stop_signal()

        queues_names = ["raw", "msg_in", "msg_out", "app", "conn"]
        for name in queues_names:
            queue = getattr(kytos_buffers, name)
            assert queue._reject_new_events
        coros = []
        for name in queues_names:
            queue = getattr(kytos_buffers, name)
            queue._queue.close()
            coros.append(queue._queue.wait_closed())
        await asyncio.gather(*coros)
