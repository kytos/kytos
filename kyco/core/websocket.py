"""Module with WebSockets."""
import asyncio
import json
import logging
from abc import abstractmethod
from io import StringIO
from threading import Thread
import websockets
from kyco.utils import log_fmt

# hide websocket logs
log = logging.getLogger('websockets.protocol')
log.setLevel(logging.ERROR)


class WebSocket(Thread):
    """Websocket class is used to serve a websocket."""

    def __init__(self, **kwargs):
        """The contructor of this class use the below params.

        Args:
            host (str): name of host used.(defaults: localhost)
            port (int): number of port used to bind the server.(defaults: 6553)
        """
        Thread.__init__(self)
        self.host = kwargs.get('host', '0.0.0.0')
        self.port = kwargs.get('port', 6553)
        self.event_loop = None
        self.is_running = False

    @abstractmethod
    @asyncio.coroutine
    def handle_msg(self, websocket, path):
        """Abstract method used to handle websocket messages.

        Args:
            websocket (websocket.server): websocket.server used.
            path(string): path of the websocket.server.
        """
        pass

    def run(self):
        """Method used to create and wait requets."""
        try:
            self.websocket = websockets.serve(self.handle_msg,
                                              self.host, self.port)
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            self.is_running = True
            self.event_loop.run_until_complete(self.websocket)
            self.event_loop.run_forever()
        finally:
            self.event_loop.close()
            self.websocket.close()

    def shutdown(self):
        """Method used to stop de websocket."""
        self.event_loop.stop()


class LogWebSocket(WebSocket):
    """LogWebSocket is used to serve a kyco logs."""

    def __init__(self, **kwargs):
        """The contructor of this class use the below params.

        Args:
            host (str): name of host used.(defaults: localhost)
            port (int): number of port used to bind the server.(defaults: 8765)
        """
        kwargs['port'] = kwargs.get('port',8765)
        self.stream = kwargs.get('stream',StringIO())
        self.logs = []
        self.buff = ""

        super().__init__(**kwargs)

    @asyncio.coroutine
    def handle_msg(self, websocket, path):
        """Method used to send logs from registered logs.

        Args:
            websocket (websocket.server): websocket.server used.
            path(string): path of the websocket.server.
        """
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
