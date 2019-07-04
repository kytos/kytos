"""Async TCP Server tests."""

import asyncio
import errno
import logging

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
            ("atcp_server", logging.INFO, "Socket timeout: 'unit_tests'"),
            ("atcp_server", logging.INFO, "Socket closed: 'unit_tests'"),
        ]
