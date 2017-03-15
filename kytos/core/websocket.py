"""Module to abstract a WebSockets."""
import asyncio
import json
import logging
from io import StringIO
from threading import Thread

import websockets

from kytos.helpers import log_fmt

# hide websocket logs
log = logging.getLogger('websockets.protocol')
log.setLevel(logging.ERROR)


class WebSocket(Thread):
    """Websocket class is used to serve a websocket."""

    def __init__(self, **kwargs):
        """The contructor of this class use the below params.

        Parameters:
            host (str): name of host used.(defaults: "0.0.0.0")
            port (int): number of port used to bind the server.(defaults: 6553)
        """
        Thread.__init__(self)
        self.host = kwargs.get('host', '0.0.0.0')
        self.port = kwargs.get('port', 6553)
        self.event_loop = None
        self.is_running = False
        self.turning_off = False
        self.websocket = None
        self.future = None

    @asyncio.coroutine
    def handle_connection(self, websocket, path):
        """Abstract method used to handle websocket messages."""
        pass

    @asyncio.coroutine
    def verify_turning_off(self, future):
        """Task to verify if thread is turning_off."""
        yield from asyncio.sleep(1)
        if self.turning_off is True:
            self.event_loop.stop()
        else:
            asyncio.ensure_future(self.verify_turning_off(self.future))

    def run(self):
        """Method used to create and wait requets."""
        try:
            self.websocket = websockets.serve(self.handle_connection,
                                              self.host, self.port)
            self.event_loop = asyncio.new_event_loop()

            asyncio.set_event_loop(self.event_loop)
            self.future = asyncio.Future()
            asyncio.ensure_future(self.verify_turning_off(self.future))

            self.is_running = True
            self.event_loop.run_until_complete(self.websocket)
            self.event_loop.run_forever()
            self.is_running = False
        finally:
            self.websocket.close()
            self.event_loop.close()

    def shutdown(self):
        """Method used to stop de websocket."""
        self.turning_off = True
        while self.is_alive():
            pass


class LogWebSocket(WebSocket):
    """LogWebSocket is used to serve a kytos logs."""

    def __init__(self, **kwargs):
        """The contructor of this class use the below params.

        Args:
            host (str): name of host used.(defaults: localhost)
            port (int): number of port used to bind the server.(defaults: 8765)
        """
        kwargs['port'] = kwargs.get('port', 8765)
        self.stream = kwargs.get('stream', StringIO())
        self.logs = []
        self.buff = ""
        super().__init__(**kwargs)

    @asyncio.coroutine
    def handle_connection(self, websocket, path):
        """Method used to send logs from registered logs."""
        data = yield from websocket.recv()
        data = json.loads(data)
        self.stream.seek(0)
        msg = self.stream.read()
        self.stream.truncate(0)
        self.buff += msg

        if data['type'] == "full_buff":
            msg = self.buff

        if len(self.buff) > 10**5:
            self.buff = msg
        yield from websocket.send(json.dumps({'msg': msg}))

    def register_log(self, log=None):
        """Method used to register new logs.

        Args:
            log (class `logging.Logger`): logger object that will be heard.
        """
        if log and log.name not in self.logs:
            streaming = logging.StreamHandler(self.stream)
            streaming.setFormatter(logging.Formatter(log_fmt()))
            log.addHandler(streaming)
            self.logs.append(log.name)
