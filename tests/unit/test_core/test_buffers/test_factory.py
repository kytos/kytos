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

