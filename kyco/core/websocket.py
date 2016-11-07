import asyncio
from abc import abstractmethod
from logging import ERROR, Formatter, getLogger, StreamHandler
from io import StringIO
from threading import Thread
from kyco.utils import log_fmt
import websockets

# hide websocket logs
log = getLogger('websockets.protocol')
log.setLevel(ERROR)

class WebSocket(Thread):
    """Websocket class is used to serve a websocket."""

    def __init__(self, **kwargs):
        """The contructor of this class use the below params.

        Args:
            host (str): name of host used.(defaults: localhost)
            port (int): number of port used to bind the server.(defaults: 6553)
        """
        Thread.__init__(self)
        self.host = kwargs.get('host','0.0.0.0')
        self.port = kwargs.get('port', 6553)
        self.event_loop = None
        self.is_running = False

    @abstractmethod
    @asyncio.coroutine
    def handle_msg(self,websocket, path):
        """Abstract method used to handle websocket messages.This method is
        asynchronous.

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

    stream = None
    def __init__(self, **kwargs):
        """The contructor of this class use the below params.

        Args:
            host (str): name of host used.(defaults: localhost)
            port (int): number of port used to bind the server.(defaults: 8765)
        """
        kwargs['port'] = kwargs.get('port',8765)
        self.stream = kwargs.get('stream',StringIO())

        super().__init__(**kwargs)

    @asyncio.coroutine
    def handle_msg(self,websocket, path):
        """Asynchronous method used to send logs from registered logs.

        Args:
            websocket (websocket.server): websocket.server used.
            path(string): path of the websocket.server.
        """
        self.stream.seek(0)
        msg = self.stream.read()
        yield from websocket.send(msg)
        self.stream.truncate(0)

    def register_log(self, log=None):
        """Method used to register new logs.

        Args:
            log (class `logging.Logger`): logger object that will be heard.
        """
        if log:
            streaming = StreamHandler(self.stream)
            streaming.setFormatter(Formatter(log_fmt()))
            log.addHandler(streaming)
