"""Kytos Daemon tests."""

import asyncio
import logging
import os
import signal
import subprocess
import sys
import unittest

import pgrep

TEST_ADDRESS = ('127.0.0.1', 4139)

logging.basicConfig(level=logging.CRITICAL)


def all_kytosd_pids() -> set:
    """Find all kytos daemon processes."""
    # proc = subprocess.run(['/bin/ps', 'xww'],
    #                       capture_output=True, text=True)
    return set(pgrep.pgrep('-f kytosd'))


class TestKytosDaemon(unittest.TestCase):
    """Test if Kytos will start in daemon mode and receive connections."""

    def setUp(self):
        """Start Kytos Daemon."""
        # save previous kytosd pids to avoid messing with other instances
        self.old_pids = all_kytosd_pids()

        kytosd_args = [sys.executable,
                       './bin/kytosd',
                       '-l', TEST_ADDRESS[0],
                       '-P', str(TEST_ADDRESS[1]),
                       '-p', '/tmp/kytos-test-daemon.pid']
        subprocess.run(kytosd_args, check=True)

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        # give the daemon some time to go up before testing
        self.loop.run_until_complete(asyncio.sleep(4, loop=self.loop))

    def new_kytosd_pids(self) -> set:
        """Find kytosd processes spawned since setUp."""
        return all_kytosd_pids() - self.old_pids

    def test_find_process(self):
        """Look for a new kytosd process."""
        self.assertTrue(self.new_kytosd_pids(), "No kytosd process id found.")

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

    def tearDown(self):
        """Send termination signal to processes spawned by unit tests."""
        for pid in self.new_kytosd_pids():
            os.kill(pid, signal.SIGTERM)
