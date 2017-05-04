"""Basic TCP Server that will listen to port 6633."""
import logging

from socket import error as SocketError
from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn
from threading import current_thread

from pyof.v0x01.common.header import Header, Type

from kytos.core.events import KytosEvent
from kytos.core.switch import Connection

__all__ = ('KytosServer', 'KytosOpenFlowRequestHandler')

log = logging.getLogger(__name__)


class KytosServer(ThreadingMixIn, TCPServer):
    """Abstraction a TCPServer to listen packages from the network.

    This is a TCP Server that will be listening on the specific port
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
        """Constructor of KytosServer receive the parameters below.

        Parameters:
            server_address (tuple): Address which the server is listening.
                default ( ('127.0.0.1', 80) )
            RequestHandlerClass (RequestHandlerClass):
                Class that will be instantiated to handle each request.
            controller (KytosController): The controller instance.

        """
        super().__init__(server_address, RequestHandlerClass,
                         bind_and_activate=False)
        # Registering the register_event 'endpoint' on the server to be
        #   accessed on the RequestHandler
        self.controller = controller
        # self.controller_put_raw_event = controller_put_raw_event

    def serve_forever(self, poll_interval=0.5):
        """Handle requests until an explicit shutdown() request."""
        try:
            self.server_bind()
            self.server_activate()
            log.info("Kytos listening at %s:%s", self.server_address[0],
                     self.server_address[1])
            super().serve_forever(poll_interval)
        except Exception:
            log.error("Maybe you have already a Kytos instance.")
            log.error('Failed to start Kytos daemon.')
            self.server_close()
            raise


class KytosOpenFlowRequestHandler(BaseRequestHandler):
    """The socket/request handler class for our controller.

    It is instantiated once per connection between each switche and the
    controller.
    The setup class will dispatch a KytosEvent (SwitchUp?) on the controller,
    that will be processed by the Controller Core (or a Core App).
    The finish class will close the connection and dispatch a KytonEvents
    (SwitchDown?) on the controller. Or this method will be called by the
    handler of this (SwitchDown) event?
    """

    def setup(self):
        """Method used to create a new connection with client.

        This method builds a new connection, makes a new KytosEvent named
        'kytos/core.connection.new' and put this in a raw buffer.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]

        self.connection = Connection(self.ip, self.port, self.request)
        self.request.settimeout(30)
        self.exception = None
        self.holded_events = []

        event = KytosEvent(name='kytos/core.connection.new',
                           content={'source': self.connection})

        self.server.controller.buffers.raw.put(event)
        log.info("New connection from %s:%s", self.ip, self.port)

    def handle(self):
        """Handle each request generically and put that in a raw event buffer.

        This method read the Header of openflow package, read the binary data,
        then create a new KytosEvent and put this in a raw event buffer.
        """
        curr_thread = current_thread()
        header_len = 8
        while True:
            header = Header()
            binary_data, raw_header = b'', b''
            try:
                while len(raw_header) < header_len:
                    remaining = header_len - len(raw_header)
                    raw_header += self.request.recv(remaining)
                    if not raw_header:
                        break
            except InterruptedError as exception:
                self.exception = exception
                break
            else:
                if not raw_header:
                    break

            log.debug("New message from %s:%s at thread %s", self.ip,
                      self.port, curr_thread.name)

            header.unpack(raw_header)
            body_len = header.length - header_len
            log.debug('Reading the binary_data')
            try:
                while len(binary_data) < body_len:
                    remaining = body_len - len(binary_data)
                    binary_data += self.request.recv(remaining)
            except (SocketError, OSError) as exception:
                self.exception = exception
                break

            content = {'source': self.connection,
                       'header': header,
                       'binary_data': binary_data}

            event = KytosEvent(name='kytos/core.messages.openflow.new',
                               content=content)

            self.send_event(event)

    def send_event(self, event):
        """Put the event on the buffer or save it for later."""
        if self.connection.switch is None:
            message_type = event.content.get('header').message_type
            if (message_type == Type.OFPT_HELLO or
                    message_type == Type.OFPT_FEATURES_REPLY):
                self.server.controller.buffers.raw.put(event)
            else:
                self.holded_events.append(event)
        else:
            while self.holded_events:
                holded_event = self.holded_events.pop(0)
                self.server.controller.buffers.raw.put(holded_event)
            self.server.controller.buffers.raw.put(event)

    def finish(self):
        """Method is called when the client connection is finished.

        When this method is called the request is closed, a new KytosEvent is
        built with kytos/core.connection.lost name and put this in a app
        buffer.
        """
        log.info("Client %s:%s disconnected. Reason: %s",
                 self.ip, self.port, self.exception)
        self.request.close()
        content = {'source': self.connection}
        if self.exception:
            content['exception'] = self.exception

        event = KytosEvent(name='kytos/core.connection.lost',
                           content=content)
        self.server.controller.buffers.app.put(event)
