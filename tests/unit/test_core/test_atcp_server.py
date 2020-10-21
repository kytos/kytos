"""Async TCP Server tests."""

import asyncio
import errno
import logging
from unittest.mock import MagicMock, patch

from kytos.core.atcp_server import (KytosServer, KytosServerProtocol,
                                    exception_handler)

# Using "nettest" TCP port as a way to avoid conflict with a running
# Kytos server on 6653.
TEST_ADDRESS = ('127.0.0.1', 4138)


class TestKytosServer:
    """Test if a Kytos Server will go up and receive connections."""

    def setup(self):
        """Start new asyncio loop and a test TCP server."""
        # pylint: disable=attribute-defined-outside-init
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.server = KytosServer(TEST_ADDRESS, KytosServerProtocol,
                                  None, 'openflow', loop=self.loop)
        self.server.serve_forever()

    def test_connection_to_server(self):
        """Test if we really can connect to TEST_ADDRESS."""
        @asyncio.coroutine
        def wait_and_go():
            """Wait a little for the server to go up, then connect."""
            yield from asyncio.sleep(0.01, loop=self.loop)
            # reader, writer = ...
            _ = yield from asyncio.open_connection(
                *TEST_ADDRESS, loop=self.loop)

        self.loop.run_until_complete(wait_and_go())

    def test_exception_handler_oserror(self, caplog):
        """Test the TCP Server Exception Handler.

        1. create mock OSError/TimeoutError instances
        2. call exception_handler with them
        3. ensure log is OK
        """
        caplog.set_level(logging.INFO)

        exception = TimeoutError()
        context = {"exception": exception,
                   "transport": "unit_tests"}
        exception_handler(self.loop, context)

        exception2 = OSError(errno.EBADF, "Bad file descriptor")
        context2 = {"exception": exception2,
                    "transport": "unit_tests"}
        exception_handler(self.loop, context2)

        assert caplog.record_tuples == [
            ("kytos.core.atcp_server",
             logging.INFO,
             "Socket timeout: 'unit_tests'"),
            ("kytos.core.atcp_server",
             logging.INFO,
             "Socket closed: 'unit_tests'"),
        ]


class TestKytosServerProtocol:
    """KytosServerProtocol tests."""

    def setup(self):
        """Instantiate a KytosServerProtocol."""
        # pylint: disable=attribute-defined-outside-init
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.connection = MagicMock()
        self.connection.address = 'addr'
        self.connection.port = 123

        self.server_protocol = KytosServerProtocol()
        self.server_protocol.server = MagicMock()
        self.server_protocol.connection = self.connection

    @patch('kytos.core.atcp_server.KytosEvent')
    def test_data_received(self, mock_kytos_event):
        """Test data_received method."""
        buffers = self.server_protocol.server.controller.buffers
        self.connection.protocol.name = 'protocol'

        self.server_protocol.data_received(b'data')

        expected_content = {'source': self.connection, 'new_data': b'data'}
        expected_name = 'kytos/core.protocol.raw.in'
        mock_kytos_event.assert_called_with(content=expected_content,
                                            name=expected_name)
        buffers.raw.aput.assert_called_with(mock_kytos_event.return_value)

    @patch('kytos.core.atcp_server.KytosEvent')
    def test_connection_lost(self, mock_kytos_event):
        """Test connection_lost method."""
        buffers = self.server_protocol.server.controller.buffers
        self.connection.protocol.name = 'protocol'

        self.server_protocol.connection_lost('exc')

        self.connection.close.assert_called()
        expected_content = {'source': self.connection, 'exception': 'exc'}
        expected_name = 'kytos/core.protocol.connection.lost'
        mock_kytos_event.assert_called_with(content=expected_content,
                                            name=expected_name)
        buffers.app.aput.assert_called_with(mock_kytos_event.return_value)
