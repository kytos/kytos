"""Async TCP Server tests."""

import asyncio
import errno
import logging
from unittest.mock import MagicMock

from kytos.core.atcp_server import (KytosServer, KytosServerProtocol,
                                    exception_handler)

# pylint: disable=protected-access


class TestKytosServer:
    """Test if a Kytos Server will go up and receive connections."""

    def setup_method(self):
        """Start new asyncio loop and a test TCP server."""
        # pylint: disable=attribute-defined-outside-init
        self._test_address = ('127.0.0.1', 4138)

    async def test_connection_to_server(self):
        """Test if we really can connect to TEST_ADDRESS."""
        server = KytosServer(self._test_address, KytosServerProtocol,
                             None, "openflow")
        server.serve_forever()

        async def wait_and_go():
            """Wait a little for the server to go up, then connect."""
            await asyncio.sleep(0.01)
            # reader, writer = ...
            _ = await asyncio.open_connection(*self._test_address)

        await wait_and_go()
        server.shutdown()

    async def test_exception_handler_oserror(self, caplog):
        """Test the TCP Server Exception Handler.

        1. create mock OSError/TimeoutError instances
        2. call exception_handler with them
        3. ensure log is OK
        """
        server = KytosServer(self._test_address, KytosServerProtocol,
                             None, "openflow")
        server.serve_forever()

        caplog.set_level(logging.INFO)

        exception = TimeoutError()
        context = {"exception": exception,
                   "transport": "unit_tests"}
        exception_handler(server.loop, context)

        exception2 = OSError(errno.EBADF, "Bad file descriptor")
        context2 = {"exception": exception2,
                    "transport": "unit_tests"}
        exception_handler(server.loop, context2)
        server.shutdown()

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

    def setup_method(self):
        """Instantiate a KytosServerProtocol."""
        # pylint: disable=attribute-defined-outside-init
        self.connection = MagicMock()
        self.connection.address = 'addr'
        self.connection.port = 123

    async def test_data_received(self):
        """Test data_received method."""
        server_protocol = KytosServerProtocol()
        server_protocol._loop = MagicMock()
        server_protocol.server = MagicMock()
        server_protocol.connection = self.connection

        buffers = server_protocol.server.controller.buffers
        self.connection.protocol.name = 'protocol'
        server_protocol.data_received(b'data')
        expected_content = {'source': self.connection, 'new_data': b'data'}
        expected_name = 'kytos/core.protocol.raw.in'
        assert buffers.raw.aput.call_count == 1
        event = buffers.raw.aput.call_args[0][0]
        assert event.name == expected_name
        assert event.content == expected_content

    async def test_connection_lost(self):
        """Test connection_lost method."""
        server_protocol = KytosServerProtocol()
        server_protocol._loop = MagicMock()
        server_protocol.server = MagicMock()
        server_protocol.connection = self.connection

        buffers = server_protocol.server.controller.buffers
        self.connection.protocol.name = 'protocol'

        server_protocol.connection_lost('exc')
        self.connection.close.assert_called()
        expected_content = {'source': self.connection, 'exception': 'exc'}
        expected_name = 'kytos/core.protocol.connection.lost'
        assert buffers.conn.aput.call_count == 1
        event = buffers.conn.aput.call_args[0][0]
        assert event.name == expected_name
        assert event.content == expected_content
