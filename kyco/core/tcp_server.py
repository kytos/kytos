"""Basic TCP Server that will listen to port 6633."""
import logging

from socket import error as SocketError
from socketserver import ThreadingMixIn
from socketserver import BaseRequestHandler
from socketserver import TCPServer
from threading import current_thread

# TODO: Fix version scheme
from pyof.v0x01.common.header import Header

from kyco.core.events import KycoRawMessageOutError
from kyco.core.events import KycoMessageOutError
from kyco.core.events import KycoNewConnection
from kyco.core.events import KycoConnectionLost
from kyco.core.events import KycoRawOpenFlowMessage

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
                 #controller_put_raw_event):
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
        content = {'request': self.request}  # request = socket
        connection_id = (self.ip, self.port)
        event = KycoNewConnection(content=content, connection_id=connection_id)
        self.server.controller.buffers.raw.put(event)
        log.info("New connection from %s:%s", self.ip, self.port)

    def handle(self):
        curr_thread = current_thread()
        header_len = 8
        connected = True
        try:
            while connected:
                # TODO: How to consider the OpenFlow version here?
                header = Header()
                binary_data = b''

                raw_header = self.request.recv(8)
                if not raw_header:
                    log.info("Client %s:%s disconnected", self.ip, self.port)
                    connected = False
                    break

                while len(raw_header) < header_len:
                    raw_header += self.request.recv(header_len - len(raw_header))

                log.debug("New message from %s:%s at thread %s", self.ip,
                          self.port, curr_thread.name)

                header.unpack(raw_header)

                message_size = header.length - header_len
                if message_size > 0:
                    log.debug('Reading the binary_data')
                    binary_data += self.request.recv(message_size)

                # TODO: Do we need other informations from the network packet?
                content = {'header': header, 'binary_data': binary_data}
                connection_id = (self.ip, self.port)
                event = KycoRawOpenFlowMessage(content=content,
                                               connection_id=connection_id)
                self.server.controller.buffers.raw.put(event)
        except (SocketError, OSError) as exception:
            # TODO: Client disconnected is the only possible reason?
            log.info("Client %s:%s disconnected", self.ip, self.port)
            error_content = {'destination': (self.ip, self.port),
                             'exception': exception, 'event': None}
            event = KycoMessageOutError(content=error_content)
            # Wrapping up the event with a container that can be inserted on
            # the raw buffer
            wrapper = KycoRawMessageOutError(content={'event': event},
                                             connection_id=(self.ip, self.port)
                                             )
            self.server.controller.buffers.raw.put(wrapper)

    def finish(self):
        log.info("Connection lost from %s:%s", self.ip, self.port)
        connection_id = (self.ip, self.port)
        event = KycoConnectionLost(connection_id=connection_id)
        self.server.controller.buffers.raw.put(event)
