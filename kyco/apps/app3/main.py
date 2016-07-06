import time


class App3(object):

    def __init__(self):
        self.app_id = 3
        self.name = 'third_app'
        self.counted_value = 0
        self.received_messages = 0
        self.processed_messages = 0

    def status(self):
        return "[App {}] RM: {} | PM: {}".format(self.app_id,
                                                 self.received_messages,
                                                 self.processed_messages)

    def handle_event(self, event):
        addr = event[0]
        data = event[1]
        message_id = self.received_messages
        self.received_messages += 1
        print(self.status(), " | Message received ", message_id, " from ", addr)
        time.sleep(1*self.app_id + 20/(data+self.app_id))
        self.processed_messages += 1
        print(self.status(), " | Message processed ", message_id, " from ", addr)
