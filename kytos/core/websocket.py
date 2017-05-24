"""WebSocket abstraction."""
import logging

__all__ = ('WebSocketHandler')


class WebSocketHandler:
    """Log handler that logs to web socket."""

    @classmethod
    def get_handler(cls, socket):
        """Output logs to a web socket, filtering unwanted messages.

        Args:
            socket: socketio socket.
            stream: Object that supports ``write()`` and ``flush()``.
        """
        stream = WebSocketStream(socket)
        handler = logging.StreamHandler(stream)
        handler.addFilter(cls._filter_web_requests)
        return handler

    @staticmethod
    def _filter_web_requests(record):
        """Only allow web server messages with level higher than info.

        Do not print web requests (INFO level) to avoid infinit loop when
        printing the logs in the web interface with long-polling mode.
        """
        return record.name != 'werkzeug' or record.levelno > logging.INFO


class WebSocketStream:
    """Make loggers write to web socket."""

    def __init__(self, socketio):
        """Receive the socket to write to."""
        self._io = socketio
        self._content = ''

    def write(self, content):
        """Store a new line."""
        self._content += content

    def flush(self):
        """Send lines and reset the content."""
        lines = self._content.split('\n')[:-1]
        self._content = ''
        self._io.emit('show logs', lines, room='log')
