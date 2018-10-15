"""Async TCP Server tests."""

import asyncio
import logging
import unittest

from kytos.core.atcp_server import KytosServer, KytosServerProtocol

# from unittest.mock import Mock


logging.basicConfig(level=logging.CRITICAL)

# Using "nettest" TCP port as a way to avoid conflict with a running
# Kytos server on 6633.
TEST_ADDRESS = ('127.0.0.1', 4138)


class TestKytosServer(unittest.TestCase):
    """"Test if a Kytos Server will go up and receive connections."""
    def setUp(self):
        """Start new asyncio loop and a test TCP server."""
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
