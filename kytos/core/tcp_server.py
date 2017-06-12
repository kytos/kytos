"""Basic TCP Server that will listen to port 6633."""
import logging
from socket import error as SocketError
from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn
from threading import current_thread

from kytos.core.connection import CONNECTION_STATE, Connection
from kytos.core.events import KytosEvent

__all__ = ('KytosServer', 'KytosRequestHandler')

log = logging.getLogger(__name__)


class KytosServer(ThreadingMixIn, TCPServer):
    """Abstraction of a TCPServer to listen to packages from the network.

    The KytosServer will listen on the specified port
    for any new TCP request from the network and then instantiate the
    specified RequestHandler to handle the new request.
    It creates a new thread for each Handler.
    """

    allow_reuse_address = True
    main_threads = {}

    def __init__(self, server_address, RequestHandlerClass, controller):
        """Constructor of KytosServer.

        Args:
            server_address (tuple): Address which the server is listening.
                example: ('127.0.0.1', 80)
            RequestHandlerClass (RequestHandlerClass):
                Class that will be instantiated to handle each request.
            controller (KytosController): The controller instance.

        """
        super().__init__(server_address, RequestHandlerClass,
                         bind_and_activate=False)
        self.controller = controller

    def serve_forever(self, poll_interval=0.5):
        """Handle requests until an explicit shutdown() is called."""
        try:
            self.server_bind()
            self.server_activate()
            log.info("Kytos listening at %s:%s", self.server_address[0],
                     self.server_address[1])
            super().serve_forever(poll_interval)
        except Exception:
            log.error('Failed to start Kytos TCP Server.')
            self.server_close()
            raise


class KytosRequestHandler(BaseRequestHandler):
    """The socket/request handler class for our controller.

    It is instantiated once per connection between each switch and the
    controller.
    The setup method will dispatch a KytosEvent (kytos/core.connection.new) on
    the controller, that will be processed by a Core App.
    The finish method will close the connection and dispatch a KytonEvents
    (kytos/core.connection.closed) on the controller.
    """

    known_ports = {
        6633: 'openflow'
    }

    def __init__(self, request, client_address, server):
        """Initialize the request handler."""
        super().__init__(request, client_address, server)
        self.connection = None

    def setup(self):
        """Method used to setup the new connection.

        This method builds a new controller Connection, and places a
        'kytos/core.connection.new' KytosEvent in the app buffer.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]

        log.info("New connection from %s:%s", self.ip, self.port)

        self.connection = Connection(self.ip, self.port, self.request) # noqa
        server_port = self.server.server_address[1]
        if server_port in self.known_ports:
            protocol_name = self.known_ports[server_port]
        else:
            protocol_name = f'{server_port:04d}'
        self.connection.protocol.name = protocol_name

        self.request.settimeout(30)
        self.exception = None

        event_name = \
            f'kytos/core.{self.connection.protocol.name}.connection.new'
        event = KytosEvent(name=event_name,
                           content={'source': self.connection})

        self.server.controller.buffers.app.put(event)

    def handle(self):
        """Handle each request and places its data in the raw event buffer.

        This method loops reading the binary data from the connection socket,
        and placing a 'kytos/core.messages.new' KytosEvent in the raw event
        buffer.
        """
        curr_thread = current_thread()
        MAX_SIZE = 2**16
        while True:
            try:
                new_data = self.request.recv(MAX_SIZE)
            except (SocketError, OSError, InterruptedError,
                    ConnectionResetError) as exception:
                self.exception = exception
                log.debug('Socket handler exception while reading: %s',
                          exception)
                break
            if new_data == b'':
                self.exception = 'Request closed by client.'
                break

            log.debug("New data from %s:%s at thread %s", self.ip,
                      self.port, curr_thread.name)

            content = {'source': self.connection,
                       'new_data': new_data}
            event_name = \
                f'kytos/core.{self.connection.protocol.name}.raw.in'
            event = KytosEvent(name=event_name,
                               content=content)

            self.server.controller.buffers.raw.put(event)

    def finish(self):
        """Method is called when the client connection is finished.

        This method closes the connection socket and generates a
        'kytos/core.connection.lost' KytosEvent in the App buffer.
        """
        log.info("Connection lost with Client %s:%s. Reason: %s",
                 self.ip, self.port, self.exception)
        self.connection.state = CONNECTION_STATE.FINISHED
        self.connection.close()
        content = {'source': self.connection}
        if self.exception:
            content['exception'] = self.exception
        event_name = \
            f'kytos/core.{self.connection.protocol.name}.connection.lost'
        event = KytosEvent(name=event_name,
                           content=content)
        self.server.controller.buffers.app.put(event)
