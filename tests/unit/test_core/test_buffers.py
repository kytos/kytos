"""Test kytos.core.buffers module."""
import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, patch

from kytos.core.buffers import KytosBuffers, KytosEventBuffer


# pylint: disable=protected-access
class TestKytosEventBuffer(TestCase):
    """KytosEventBuffer tests."""

    def setUp(self):
        """Instantiate a KytosEventBuffer."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.kytos_event_buffer = KytosEventBuffer('name', loop=self.loop)

    @staticmethod
    def create_event_mock(name='any'):
        """Create a new event mock."""
        event = MagicMock()
        event.name = name
        return event

    def test_put_get(self):
        """Test put and get methods."""
        event = self.create_event_mock()

        self.kytos_event_buffer.put(event)
        queue_event = self.kytos_event_buffer.get()

        self.assertEqual(queue_event, event)

    def test_put__shutdown(self):
        """Test put method to shutdown event."""
        event = self.create_event_mock('kytos/core.shutdown')
        self.kytos_event_buffer.put(event)

        self.assertTrue(self.kytos_event_buffer._reject_new_events)

    def test_aput(self):
        """Test aput async method."""
        event = MagicMock()
        event.name = 'kytos/core.shutdown'

        self.loop.run_until_complete(self.kytos_event_buffer.aput(event))

        self.assertTrue(self.kytos_event_buffer._reject_new_events)

    def test_aget(self):
        """Test aget async method."""
        event = self.create_event_mock()
        self.kytos_event_buffer._queue.sync_q.put(event)

        expected = self.loop.run_until_complete(self.kytos_event_buffer.aget())

        self.assertEqual(event, expected)

    @patch('janus._SyncQueueProxy.task_done')
    def test_task_done(self, mock_task_done):
        """Test task_done method."""
        self.kytos_event_buffer.task_done()

        mock_task_done.assert_called()

    @patch('janus._SyncQueueProxy.join')
    def test_join(self, mock_join):
        """Test join method."""
        self.kytos_event_buffer.join()

        mock_join.assert_called()

    def test_qsize(self):
        """Test qsize method to empty and with one event in query."""
        qsize_1 = self.kytos_event_buffer.qsize()

        event = self.create_event_mock()
        self.kytos_event_buffer._queue.sync_q.put(event)

        qsize_2 = self.kytos_event_buffer.qsize()

        self.assertEqual(qsize_1, 0)
        self.assertEqual(qsize_2, 1)

    def test_empty(self):
        """Test empty method to empty and with one event in query."""
        empty_1 = self.kytos_event_buffer.empty()

        event = self.create_event_mock()
        self.kytos_event_buffer._queue.sync_q.put(event)

        empty_2 = self.kytos_event_buffer.empty()

        self.assertTrue(empty_1)
        self.assertFalse(empty_2)

    @patch('janus._SyncQueueProxy.full')
    def test_full(self, mock_full):
        """Test full method to full and not full query."""
        mock_full.side_effect = [False, True]

        full_1 = self.kytos_event_buffer.full()
        full_2 = self.kytos_event_buffer.full()

        self.assertFalse(full_1)
        self.assertTrue(full_2)


class TestKytosBuffers(TestCase):
    """KytosBuffers tests."""

    def setUp(self):
        """Instantiate a KytosBuffers."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        self.kytos_buffers = KytosBuffers(loop=self.loop)

    def test_send_stop_signal(self):
        """Test send_stop_signal method."""
        self.kytos_buffers.send_stop_signal()

        self.assertTrue(self.kytos_buffers.raw._reject_new_events)
        self.assertTrue(self.kytos_buffers.msg_in._reject_new_events)
        self.assertTrue(self.kytos_buffers.msg_out._reject_new_events)
        self.assertTrue(self.kytos_buffers.app._reject_new_events)
