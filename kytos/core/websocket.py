"""Module to abstract a WebSockets."""
import sys
import traceback
import asyncio
import logging
from io import StringIO
from threading import Thread
from flask_socketio import emit
from kytos.utils import log_fmt

# hide websocket logs
engineio_logs = logging.getLogger('engineio')
engineio_logs.setLevel(logging.ERROR)
socketio_logs = logging.getLogger('socketio')
socketio_logs.setLevel(logging.ERROR)

class LogWebSocket:

    def __init__(self, *args, **kwargs):
        self.stream = kwargs.get('stream', StringIO())
        self.buffer_max_size = kwargs.get('buffer_max_size', 5000)
        self.loggers = []
        self.buff = []

    @property
    def events(self):
        return [('show logs', self.handle_messages, '/logs')]

    def update_buffer(self):
        self.stream.seek(0)
        msg = self.stream.read().split('\n')[:-1]

        if len(msg) == 0 :
            return

        self.buff.extend(msg)
        self.stream.truncate(0)

        if len(self.buff) >= self.buffer_max_size:
            new_size = self.buffer_max_size/2
            self.buff = self.buff[new_size:]

    def handle_messages(self, json):
        current_line = json.get('current_line',0)
        self.update_buffer()
        result = {"buff":  self.buff[current_line:],
                  "last_line": len(self.buff)}
        emit('show logs', result)

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
