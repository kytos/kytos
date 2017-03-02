"""Module to abstract a WebSockets."""
import sys
import contextlib
import traceback
import asyncio
import json
import logging
from io import StringIO
from threading import Thread

import websockets
from websockets.exceptions import ConnectionClosed

from kytos.core.helpers import log_fmt

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
        self.turning_off = False
        self.websocket = None
        self.future = None

    @property
    def is_running(self):
        """Method used to known if the websocket is closed."""
        return self.websocket.closed() is False

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

            self._server = self.event_loop.run_until_complete(self.websocket)
            self.event_loop.run_forever()
        finally:
            self.event_loop.call_soon(self._server.close)
            self.event_loop.run_until_complete(self._server.wait_closed())

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
        self.loggers = []
        self.buff = ""
        super().__init__(**kwargs)

    @asyncio.coroutine
    def handle_connection(self, websocket, path):
        """Method used to handle websockets connecteds.

        This method will receive a json using the format:

        {
          "seek": 23
        }

        If the seek is 0 the full buff from log will be send, otherwise only
        the last log registered will be send.

        The response is a json with the format:
        {
          "msg": "<Log message>"
        }

        """
        while True:
            try:
                data = yield from websocket.recv()
                data = json.loads(data)
                self.stream.seek(0)
                msg = self.stream.read()
                self.stream.truncate(0)
                self.buff += msg

                if data['seek'] == 0 :
                    msg = self.buff

                if len(self.buff) > 10**5:
                    self.buff = msg[10**5/2:]

                yield from websocket.send(json.dumps({'msg': msg}))
            except ConnectionClosed:
                pass

    def register_log(self, logger=None):
        """Method used to register new loggers.

        Args:
            logger (class `logging.Logger`): logger object that will be heard.
        """
        if logger and logger.name not in self.loggers:
            streaming = logging.StreamHandler(self.stream)
            streaming.setFormatter(logging.Formatter(log_fmt()))
            logger.addHandler(streaming)
            self.loggers.append(logger.name)

class ConsoleWebSocket(WebSocket):
    """ConsoleWebSocket is used to serve a kyco python console."""

    def __init__(self, **kwargs):
        """The contructor of this class use the below params.

        Args:
            host (str): name of host used.(defaults: localhost)
            port (int): number of port used to bind the server.(defaults: 8766)
            controller (KytosController):
        """
        kwargs['port'] = kwargs.get('port', 8766)
        self.controller = kwargs.get('controller', None)
        super().__init__(**kwargs)

    @asyncio.coroutine
    def handle_connection(self, websocket, path):
        """Method used to handle websockets connecteds."""
        while True:
            try:
                cmd = yield from websocket.recv()
                with self.stdoutIO() as f:
                    try:
                        exec(cmd)
                    except Exception as err:
                        print(traceback.format_exc())

                print("message {}".format(cmd))
                result = f.getvalue()
                print(result)
                yield from websocket.send(result)
            except ConnectionClosed:
                pass

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        """Method used to redirect the default stdout to custom stdout.

        The default custom stdout is a StringIO instance.
        """
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old
