"""Module to abstract a WebSockets."""
import logging
from io import StringIO

from flask_socketio import emit


class LogWebSocket:
    """Class used to send logs using socketio."""

    def __init__(self, **kwargs):
        """The constructor of LogWebSocket receive the parameters below.

        Args:
           stream(StringIO()):   buffer used to store the logs
           buffer_max_size(int): Max size used by stream.
        """
        self.stream = kwargs.get('stream', StringIO())
        self.buffer_max_size = kwargs.get('buffer_max_size', 5000)
        self.buff = []
        self._set_log_level(logging.ERROR)

    @staticmethod
    def _set_log_level(level):
        for name in 'engineio', 'socketio':
            log = logging.getLogger(name)
            log.setLevel(level)

    @property
    def events(self):
        """Method used to return all channels used by LogWebsocket instance."""
        return [('show logs', self.handle_messages, '/logs')]

    def update_buffer(self):
        """Method used to update the buffer from stream of logs."""
        self.stream.seek(0)
        msg = self.stream.read().split('\n')[:-1]

        if not msg:
            return

        self.buff.extend(msg)
        self.stream.truncate(0)

        if len(self.buff) >= self.buffer_max_size:
            new_size = self.buffer_max_size/2
            self.buff = self.buff[new_size:]

    def handle_messages(self, json):
        """Method used to send logs to clients."""
        current_line = json.get('current_line', 0)
        self.update_buffer()
        result = {"buff":  self.buff[current_line:],
                  "last_line": len(self.buff)}
        emit('show logs', result)
