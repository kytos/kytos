"""Test kytos.core.buffers.factory module."""
from unittest.mock import MagicMock

import pytest

from kytos.core.buffers import factory


class TestBufferFromConfig:
    """Tests for from_buffer_config"""

    async def test_defaults(self, monkeypatch):
        """Tests creating a buffer from default values"""
        name = 'Test Unit 1'
        input_config = {}

        buffer_cls_mock = MagicMock()
        buffer_mock = MagicMock()
        buffer_cls_mock.return_value = buffer_mock

        process_queue_mock = MagicMock()
        queue_mock = MagicMock()
        process_queue_mock.return_value = queue_mock

        monkeypatch.setattr(
            "kytos.core.buffers.factory.KytosEventBuffer",
            buffer_cls_mock
        )
        monkeypatch.setattr(
            "kytos.core.buffers.factory.process_queue",
            process_queue_mock
        )
        monkeypatch.setattr(
            "kytos.core.buffers.factory.extension_processors",
            {}
        )

        result_buffer = factory.buffer_from_config(name, input_config)

        assert result_buffer == buffer_mock
        buffer_cls_mock.assert_called_once_with(
            name,
            queue=queue_mock,
        )
        process_queue_mock.assert_called_once_with(
            {}
        )

    async def test_bad_extension(self, monkeypatch):
        """Tests creating a buffer with an invalid extension"""

        name = 'Test Unit 2'
        input_config = {
            'extensions': [
                {
                    'type': 'Nonexistant',
                },
            ]
        }

        buffer_cls_mock = MagicMock()
        buffer_mock = MagicMock()
        buffer_cls_mock.return_value = buffer_mock

        process_queue_mock = MagicMock()
        queue_mock = MagicMock()
        process_queue_mock.return_value = queue_mock

        monkeypatch.setattr(
            "kytos.core.buffers.factory.KytosEventBuffer",
            buffer_cls_mock
        )
        monkeypatch.setattr(
            "kytos.core.buffers.factory.process_queue",
            process_queue_mock
        )
        monkeypatch.setattr(
            "kytos.core.buffers.factory.extension_processors",
            {}
        )

        with pytest.raises(KeyError):
            factory.buffer_from_config(name, input_config)

    async def test_good_extension(self, monkeypatch):
        """Tests creating a buffer with an valid extension"""

        name = 'Test Unit 3'
        input_config = {
            'extensions': [
                {
                    'type': 'existant',
                    'args': 'Unique value'
                },
            ]
        }

        buffer_cls_mock = MagicMock()
        buffer_mock = MagicMock()
        buffer_cls_mock.return_value = buffer_mock

        process_queue_mock = MagicMock()
        queue_mock = MagicMock()
        process_queue_mock.return_value = queue_mock

        extension_processor_mock = MagicMock()
        extended_instance_mock = MagicMock
        extension_processor_mock.return_value = extended_instance_mock

        monkeypatch.setattr(
            "kytos.core.buffers.factory.KytosEventBuffer",
            buffer_cls_mock
        )
        monkeypatch.setattr(
            "kytos.core.buffers.factory.process_queue",
            process_queue_mock
        )
        monkeypatch.setattr(
            "kytos.core.buffers.factory.extension_processors",
            {'existant': extension_processor_mock}
        )

        result_buffer = factory.buffer_from_config(name, input_config)

        assert result_buffer == extended_instance_mock
        extension_processor_mock.assert_called_once_with(
            buffer_mock,
            'Unique value'
        )
        buffer_cls_mock.assert_called_once_with(
            name,
            queue=queue_mock,
        )
        process_queue_mock.assert_called_once_with(
            {}
        )

    async def test_queue_config(self, monkeypatch):
        """Tests creating a buffer with queue configurations"""
        name = 'Test Unit 4'
        input_config = {
            'queue': 'Unique value 2'
        }

        buffer_cls_mock = MagicMock()
        buffer_mock = MagicMock()
        buffer_cls_mock.return_value = buffer_mock

        process_queue_mock = MagicMock()
        queue_mock = MagicMock()
        process_queue_mock.return_value = queue_mock

        monkeypatch.setattr(
            "kytos.core.buffers.factory.KytosEventBuffer",
            buffer_cls_mock
        )
        monkeypatch.setattr(
            "kytos.core.buffers.factory.process_queue",
            process_queue_mock
        )
        monkeypatch.setattr(
            "kytos.core.buffers.factory.extension_processors",
            {}
        )

        result_buffer = factory.buffer_from_config(name, input_config)

        assert result_buffer == buffer_mock
        buffer_cls_mock.assert_called_once_with(
            name,
            queue=queue_mock,
        )
        process_queue_mock.assert_called_once_with(
            'Unique value 2'
        )


class TestProcessQueue:
    """Tests for process_queue"""

    def test_defaults(self, monkeypatch):
        """Tests creating a queue from default values"""
        input_config = {}

        mock_queue_cls = MagicMock()
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        mock_priority_queue_cls = MagicMock()
        mock_priority_queue = MagicMock()
        mock_priority_queue_cls.return_value = mock_priority_queue

        monkeypatch.setattr(
            "kytos.core.buffers.factory.queue_classes",
            {
                "queue": mock_queue_cls,
                "priority": mock_priority_queue_cls,
            }
        )

        result_queue = factory.process_queue(input_config)

        assert result_queue == mock_queue

        mock_queue_cls.assert_called_once_with(maxsize=0)

    def test_set_type(self, monkeypatch):
        """Tests creating a queue with a specified type"""
        input_config = {
            'type': 'priority'
        }

        mock_queue_cls = MagicMock()
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        mock_priority_queue_cls = MagicMock()
        mock_priority_queue = MagicMock()
        mock_priority_queue_cls.return_value = mock_priority_queue

        monkeypatch.setattr(
            "kytos.core.buffers.factory.queue_classes",
            {
                "queue": mock_queue_cls,
                "priority": mock_priority_queue_cls,
            }
        )

        result_queue = factory.process_queue(input_config)

        assert result_queue == mock_priority_queue

        mock_priority_queue_cls.assert_called_once_with(maxsize=0)

    def test_set_size(self, monkeypatch):
        """Tests creating a queue with a given maxsize"""
        maxsize = 39
        input_config = {
            'maxsize': maxsize,
        }

        mock_queue_cls = MagicMock()
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        mock_priority_queue_cls = MagicMock()
        mock_priority_queue = MagicMock()
        mock_priority_queue_cls.return_value = mock_priority_queue

        monkeypatch.setattr(
            "kytos.core.buffers.factory.queue_classes",
            {
                "queue": mock_queue_cls,
                "priority": mock_priority_queue_cls,
            }
        )

        result_queue = factory.process_queue(input_config)

        assert result_queue == mock_queue

        mock_queue_cls.assert_called_once_with(maxsize=maxsize)

    def test_set_size_threadpool(self, monkeypatch):
        """Tests creating a queue with a threadpool determined maxsize"""
        maxsize = 'threadpool_test'
        expected_size = 39
        input_config = {
            'maxsize': maxsize,
        }

        mock_queue_cls = MagicMock()
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        mock_priority_queue_cls = MagicMock()
        mock_priority_queue = MagicMock()
        mock_priority_queue_cls.return_value = mock_priority_queue

        mock_get_threadpool_max = MagicMock()
        mock_get_threadpool_max.return_value = {
            'test': expected_size,
        }

        monkeypatch.setattr(
            "kytos.core.buffers.factory.queue_classes",
            {
                "queue": mock_queue_cls,
                "priority": mock_priority_queue_cls,
            }
        )

        monkeypatch.setattr(
            "kytos.core.buffers.factory.get_thread_pool_max_workers",
            mock_get_threadpool_max
        )

        result_queue = factory.process_queue(input_config)

        assert result_queue == mock_queue

        mock_queue_cls.assert_called_once_with(maxsize=expected_size)

    def test_set_size_bad_threadpool(self, monkeypatch):
        """Tests creating a queue with a non existant threadpool for maxsize"""
        maxsize = 'threadpool_test2'
        not_expected_size = 39
        input_config = {
            'maxsize': maxsize,
        }

        mock_queue_cls = MagicMock()
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        mock_priority_queue_cls = MagicMock()
        mock_priority_queue = MagicMock()
        mock_priority_queue_cls.return_value = mock_priority_queue

        mock_get_threadpool_max = MagicMock()
        mock_get_threadpool_max.return_value = {
            'test': not_expected_size,
        }

        monkeypatch.setattr(
            "kytos.core.buffers.factory.queue_classes",
            {
                "queue": mock_queue_cls,
                "priority": mock_priority_queue_cls,
            }
        )

        monkeypatch.setattr(
            "kytos.core.buffers.factory.get_thread_pool_max_workers",
            mock_get_threadpool_max
        )

        result_queue = factory.process_queue(input_config)

        assert result_queue == mock_queue

        mock_queue_cls.assert_called_once_with(maxsize=0)

    def test_set_size_bad_str(self, monkeypatch):
        """Tests creating a queue with an invalid string"""
        maxsize = 'bad string'
        input_config = {
            'maxsize': maxsize,
        }

        mock_queue_cls = MagicMock()
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        mock_priority_queue_cls = MagicMock()
        mock_priority_queue = MagicMock()
        mock_priority_queue_cls.return_value = mock_priority_queue

        mock_get_threadpool_max = MagicMock()
        mock_get_threadpool_max.return_value = {}

        monkeypatch.setattr(
            "kytos.core.buffers.factory.queue_classes",
            {
                "queue": mock_queue_cls,
                "priority": mock_priority_queue_cls,
            }
        )

        monkeypatch.setattr(
            "kytos.core.buffers.factory.get_thread_pool_max_workers",
            mock_get_threadpool_max
        )

        with pytest.raises(TypeError):
            factory.process_queue(input_config)
