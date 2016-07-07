"""Testing for contoller"""

import importlib
import os
import sys

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

    def install_app(self):
        pass

    def load_app(self, app_name):
        path = os.path.join(APPS_DIR, app_name, 'main.py')
        module = importlib.machinery.SourceFileLoader(app_name, path)
        app = module.load_module().Main()

        app.add_to_msg_out_events_buffer = self.buffers.msg_out_events.put
        app.add_to_app_events_buffer = self.buffers.app_events.put
        self.apps.append(app)

        for event_type, listeners in app._listeners.items():
            if event_type not in self.events_listeners:
                self._events_listeners[event_type] = []
            self._events_listeners[event_type].extend(listeners)

    def load_apps(self):
        for app_name in os.listdir(APPS_DIR):
            if os.path.isdir(os.path.join(APPS_DIR, app_name)):
                self.load_app(app_name)
