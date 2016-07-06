"""Testing for contoller"""

from configparser import SafeConfigParser
from threading import Thread

from kyco.apps.app1 import App1 as _A1
from kyco.apps.app2 import App2 as _A2
from kyco.core.buffers import KycoBuffers
from kyco.core.event_handlers import raw_event_handler
from kyco.core.event_handlers import msg_in_event_handler
from kyco.core.event_handlers import msg_out_event_handler
from kyco.core.event_handlers import app_event_handler
from kyco.core.tcp_server import KycoOpenFlowRequestHandler
from kyco.core.tcp_server import KycoServer
from kyco.utils import start_logger


log = start_logger()

config = SafeConfigParser()
config.read('kyco_config.ini')
HOST = config.get('TCP', 'HOST')
PORT = config.getint('TCP', 'PORT')


class Controller(object):
    def __init__(self):
        self.apps = {}
        self._events_listeners = {}
        self.buffers = KycoBuffers()
        self._kyco_server = None
        self._threads = {}

    def start(self):
        log.info("Starting Kyco - Kytos Controller")
        self._server = KycoServer((HOST, PORT), KycoOpenFlowRequestHandler,
                                  self.buffers.raw_events.put)

        thrds = {'tcp_server': Thread(name='TCP server',
                                      target=self._server.serve_forever),
                 'raw_event_handler': Thread(name='RawEvent Handler',
                                             target=raw_event_handler,
                                             args=[self.buffers.raw_events,
                                                   self.buffers.msg_in_events,
                                                   self.buffers.app_events]),
                 'msg_in_event_handler': Thread(name='MsgInEvent Handler',
                                                target=msg_in_event_handler,
                                                args=[self.buffers.msg_in_events]),
                 'msg_out_event_handler': Thread(name='MsgOutEvent Handler',
                                                 target=msg_out_event_handler,
                                                 args=[self.buffers.msg_out_events]),
                 'app_event_handler': Thread(name='AppEvent Handler',
                                             target=app_event_handler,
                                             args=[self.buffers.app_events])}

        self._threads = thrds
        for _, thread in self._threads.items():
            thread.start()

        log.info("Loading kyco apps...")
        self.load_apps()

    def stop(self):
        self._server.socket.close()
        self._server.shutdown()
        # TODO: This is not working... How to kill the handlers threads?
        #       the join() wait the method to end,
        #       but there we have a while True...
        for _, thread in self._threads.items():
            thread.join()
    def load_apps(self):
        # TODO: FIX APP Loading....
        app1 = _A1()
        app2 = _A2()
        apps = {
            app1: [0, 2],
            app2: [1]
        }
        for app in apps:
            app.output_buffer = self.buffers.msg_out_events.put
            app.events_buffer = self.buffers.app_events.put
            for event in apps[app]:
                if event not in self._events_listeners:
                    self._events_listeners[event] = []
                self._events_listeners[event].append(app)


if __name__ == '__main__':
    controller = Controller()
    controller.start()
