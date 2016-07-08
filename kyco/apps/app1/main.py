"""First app...."""
import time
import logging

from kyco.utils import APP_MSG
from kyco.utils import KycoNApp
from kyco.utils import listen_to

log = logging.getLogger('kytos[A]')


class Main(KycoNApp):

    def setUp(self):
        self.app_id = 1
        self.name = 'first_app'
        self.counted_value = 0
        self.received_messages = 0
        self.processed_messages = 0
        self.events_buffer = None

    @listen_to('KycoMessageIn')
    def handle_event(self, event):
        addr = event[0]
        data = event[1]
        message_id = self.received_messages
        self.received_messages += 1
        log.debug(APP_MSG, self.app_id, 'Received', message_id,
                  self.received_messages, self.processed_messages,
                  addr)
        time.sleep(1*self.app_id + 20/(data+self.app_id))
        self.processed_messages += 1
        log.debug(APP_MSG, self.app_id, 'Processed', message_id,
                  self.received_messages, self.processed_messages,
                  addr)
        event_id = 1
        log.info("[App 1] Writing event on EventBuffer...")
        self.events_buffer.put((event_id, self.app_id, message_id, data, addr))

    def shutdown(self):
        pass
