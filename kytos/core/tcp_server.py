"""Basic TCP Server that will listen to port 6633."""
import logging
from socket import error as SocketError
from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn
from threading import current_thread

from kytos.core.connection import Connection, ConnectionState
from kytos.core.events import KytosEvent

__all__ = ('KytosServer', 'KytosRequestHandler')

LOG = logging.getLogger(__name__)


class KytosServer(ThreadingMixIn, TCPServer):
    """Abstraction of a TCPServer to listen to packages from the network.

    The KytosServer will listen on the specified port
    for any new TCP request from the network and then instantiate the
    specified RequestHandler to handle the new request.
    It creates a new thread for each Handler.
    """

    allow_reuse_address = True
    main_threads = {}

    def __init__(self, server_address, RequestHandlerClass, controller,
                 protocol_name):
        """Create the object without starting the server.

        Args:
            server_address (tuple): Address which the server is listening.
                example: ('127.0.0.1', 80)
            RequestHandlerClass(socketserver.BaseRequestHandler):
                Class that will be instantiated to handle each request.
            controller (:class:`~kytos.core.controller.Controller`):
                An instance of Kytos Controller class.
            protocol_name (str): Southbound protocol name that will be used
        """
        super().__init__(server_address, RequestHandlerClass,
                         bind_and_activate=False)
        self.controller = controller
        self.protocol_name = protocol_name

    def serve_forever(self, poll_interval=0.5):
        """Handle requests until an explicit shutdown() is called."""
        try:
            self.server_bind()
            self.server_activate()
            LOG.info("Kytos listening at %s:%s", self.server_address[0],
                     self.server_address[1])
            super().serve_forever(poll_interval)
        except Exception:
            LOG.error('Failed to start Kytos TCP Server.')
            self.server_close()
            raise


class KytosRequestHandler(BaseRequestHandler):
    """The socket/request handler class for our controller.

    It is instantiated once per connection between each switch and the
    controller.
    The setup method will dispatch a KytosEvent (``kytos/core.connection.new``)
    on the controller, that will be processed by a Core App.
    The finish method will close the connection and dispatch a KytonEvents
    (``kytos/core.connection.closed``) on the controller.
    """

    known_ports = {
        6633: 'openflow',
        6653: 'openflow'
    }

    def __init__(self, request, client_address, server):
        """Contructor takes the parameters below.

        Args:
            request (socket.socket):
                Request sent by client.
            client_address (tuple):
                Client address, tuple with host and port.
            server (socketserver.BaseServer):
                Server used to send messages to client.
        """
        super().__init__(request, client_address, server)
        self.connection = None

    def setup(self):
        """Create a new controller connection.

        This method builds a new controller Connection, and places a
        ``kytos/core.connection.new`` KytosEvent in the app buffer.
        """
        self.addr = self.client_address[0]
        self.port = self.client_address[1]

        LOG.info("New connection from %s:%s", self.addr, self.port)

        self.connection = Connection(self.addr, self.port, self.request)
        server_port = self.server.server_address[1]
        if self.server.protocol_name:
            self.known_ports[server_port] = self.server.protocol_name

        if server_port in self.known_ports:
            protocol_name = self.known_ports[server_port]
        else:
            protocol_name = f'{server_port:04d}'
        self.connection.protocol.name = protocol_name

        self.request.settimeout(70)
        self.exception = None

        event_name = \
            f'kytos/core.{self.connection.protocol.name}.connection.new'
        event = KytosEvent(name=event_name,
                           content={'source': self.connection})

        self.server.controller.buffers.app.put(event)

    def handle(self):
        """Handle each request and places its data in the raw event buffer.

        This method loops reading the binary data from the connection socket,
        and placing a ``kytos/core.messages.new`` KytosEvent in the raw event
        buffer.
        """
        curr_thread = current_thread()
        max_size = 2**16
        while True:
            try:
                new_data = self.request.recv(max_size)
            except (SocketError, OSError, InterruptedError,
                    ConnectionResetError) as exception:
                self.exception = exception
                LOG.debug('Socket handler exception while reading: %s',
                          exception)
                break
            if new_data == b'':
                self.exception = 'Request closed by client.'
                break

            if not self.connection.is_alive():
                continue

            LOG.debug("New data from %s:%s at thread %s", self.addr,
                      self.port, curr_thread.name)

            content = {'source': self.connection,
                       'new_data': new_data}
            event_name = \
                f'kytos/core.{self.connection.protocol.name}.raw.in'
            event = KytosEvent(name=event_name,
                               content=content)

            self.server.controller.buffers.raw.put(event)

    def finish(self):
        """Run when the client connection is finished.

        This method closes the connection socket and generates a
        ``kytos/core.connection.lost`` KytosEvent in the App buffer.
        """
        LOG.info("Connection lost with Client %s:%s. Reason: %s",
                 self.addr, self.port, self.exception)
        self.connection.state = ConnectionState.FINISHED
        self.connection.close()
        content = {'source': self.connection}
        if self.exception:
            content['exception'] = self.exception
        event_name = \
            f'kytos/core.{self.connection.protocol.name}.connection.lost'
        event = KytosEvent(name=event_name,
                           content=content)
        self.server.controller.buffers.app.put(event)
