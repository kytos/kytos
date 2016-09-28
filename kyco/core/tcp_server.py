"""Basic TCP Server that will listen to port 6633."""
import logging
from socket import error as SocketError
from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn
from threading import current_thread

# TODO: Fix version scheme
from pyof.v0x01.common.header import Header

from kyco.core.events import KycoEvent
from kyco.core.switch import Connection

__all__ = ['KycoServer', 'KycoOpenFlowRequestHandler']

log = logging.getLogger('Kyco')


class KycoServer(ThreadingMixIn, TCPServer):
    """This is a TCP Server that will be listening on the specifiec port
    (defaults to 6633) for any package that comes from the network and then
    stabilishes the socket connection to the devices (switches) when needed,
    considering a thread per connection and keeping the connection alive.
    """
    # daemon_threads = True
    allow_reuse_address = True
    main_threads = {}

    def __init__(self, server_address, RequestHandlerClass,
                 # Change after definitions on #62
                 # controller_put_raw_event):
                 controller):
        super().__init__(server_address, RequestHandlerClass,
                         bind_and_activate=False)
        # Registering the register_event 'endpoint' on the server to be
        #   accessed on the RequestHandler
        self.controller = controller
        # self.controller_put_raw_event = controller_put_raw_event

    def serve_forever(self, poll_interval=0.5):
        try:
            self.server_bind()
            self.server_activate()
            log.info("Kyco listening at {}:{}".format(self.server_address[0],
                                                      self.server_address[1]))
            super().serve_forever(poll_interval)
        except:
            self.server_close()
            raise


class KycoOpenFlowRequestHandler(BaseRequestHandler):
    """The socket/request handler class for our controller.

    It is instantiated once per connection between each switche and the
    controller.
    The setup class will dispatch a KycoEvent (SwitchUp?) on the controller,
    that will be processed by the Controller Core (or a Core App).
    The finish class will close the connection and dispatch a KytonEvents
    (SwitchDown?) on the controller. Or this method will be called by the
    handler of this (SwitchDown) event?
    """
    def setup(self):
        self.ip = self.client_address[0]
        self.port = self.client_address[1]

        self.connection = Connection(self.ip, self.port, self.request)
        self.exception = None

        event = KycoEvent(name='kyco/core.connection.new',
                          content = {'connection': self.connection})

        self.server.controller.buffers.raw.put(event)
        log.info("New connection from %s:%s", self.ip, self.port)

    def handle(self):
        curr_thread = current_thread()
        header_len = 8
        while True:
            # TODO: How to consider the OpenFlow version here?
            header = Header()
            binary_data = b''
            raw_header = b''
            try:
                while len(raw_header) < header_len:
                    raw_header += self.request.recv(header_len - len(raw_header))
            except (SocketError, OSError) as exception:
                self.exception = exception
                break

            log.debug("New message from %s:%s at thread %s", self.ip,
                      self.port, curr_thread.name)

            # TODO: Create an exception if this is not a OF message
            header.unpack(raw_header)
            body_len = header.length - header_len
            log.debug('Reading the binary_data')
            try:
                while len(binary_data) < body_len:
                    binary_data += self.request.recv(body_len - len(binary_data))
            except (SocketError, OSError) as exception:
                self.exception = exception
                break

            # TODO: Do we need other informations from the network packet?
            content = {'connection': self.connection,
                       'header': header,
                       'binary_data': binary_data}

            event = KycoEvent(name='kyco/core.messages.openflow.new',
                              content=content)

            self.server.controller.buffers.raw.put(event)

    def finish(self):
        # TODO: Client disconnected is the only possible reason?
        log.info("Client %s:%s disconnected", self.ip, self.port)
        content = {'connection': self.connection}
        if self.exception:
            content['exception'] = self.exception

        event = KycoEvent(name='kyco/core.connection.lost',
                          content=content)
        self.server.controller.buffers.app.put(event)
