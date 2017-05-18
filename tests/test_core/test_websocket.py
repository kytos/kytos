"""Test websocket log."""
from unittest import TestCase, mock

from kytos.core.websocket import LogWebSocket


class TestLogWebSocket(TestCase):
    """Test sending logs to the web interface."""

    #: int: max number of lines to return (requested by the web client)
    MAX_LINES = 3

    @classmethod
    @mock.patch('kytos.core.websocket.emit')
    def _get_new_lines(cls, current_line, emit=None):
        """Our answer to the web client.

        Args:
            current_line (str): Index of the first line to be sent.

        Returns:
            list: Log lines.
        """
        total_lines = 10
        log = LogWebSocket()

        # Simulate kytosd writing to log
        for i in range(total_lines):
            log.stream.write(f'{i}\n')

        # Simulate the request from the web client
        client_json = dict(current_line=current_line, max_lines=cls.MAX_LINES)
        log.handle_messages(client_json)

        return emit.call_args[0][1]

    def test_max_lines(self):
        """Should return no more lines than max_lines."""
        answer2client = self._get_new_lines(0)
        lines = answer2client['buff']
        self.assertEqual(self.MAX_LINES, len(lines))

    def test_continuation_content(self):
        """Should send the next line in the next request.

        Assume there are no more new messages than max_lines.
        """
        answer2client = self._get_new_lines(3)
        lines = answer2client['buff']
        self.assertListEqual(['7', '8', '9'], lines)

    def test_continuation_index(self):
        """Should return the index of the next log line to be retrieved."""
        answer2client = self._get_new_lines(3)
        next_line = answer2client['last_line']
        self.assertEqual(10, next_line)
