"""Module used to handle a API Server."""
import logging
import os
from urllib.error import URLError
from urllib.request import urlopen

from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO


class APIServer:
    """Api server used to provide Kytos Controller routes."""

    def __init__(self, app_name, debug=False):
        """Contructor of APIServer.

        This method will instantiate a server with SocketIO+Flask.

        Parameters:
            app_name(string): String representing a App Name
        """
        dirname = os.path.dirname(os.path.abspath(__file__))
        self.flask_dir = os.path.join(dirname, '../web-ui/source')
        self.log = logging.getLogger('werkzeug')
        self.set_debug(debug)

        self.app = Flask(app_name, root_path=self.flask_dir)
        self.server = SocketIO(self.app, async_mode='threading')

    def set_debug(self, debug=False):
        """Method used to set debug mode.

        Args:
            debug(bool): Boolean value to turn on/off debug mode.
        """
        if debug is True:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.WARNING)

    def run(self, *args, **kwargs):
        """Method used to run the APIServer."""
        try:
            self.server.run(self.app, *args, **kwargs)
        except OSError:
            pass

    def register_rest_endpoint(self, url, function, methods):
        r"""Register a new rest endpoint in Api Server.

        To register new endpoints is needed to have a url, function to handle
        the requests and type of method allowed.

        Parameters:
            url (string):        String with partner of route. e.g.: '/status'
            function (function): Function pointer used to handle the requests.
            methods (list):      List of request methods allowed.
                                 e.g: ['GET', 'PUT', 'POST', 'DELETE', 'PATCH']
        """
        if url not in self.rest_endpoints:
            new_endpoint_url = "/kytos{}".format(url)
            self.app.add_url_rule(new_endpoint_url, function.__name__,
                                  function, methods=methods)

    def register_websockets(self, websockets):
        """Method used to register all channels from websockets given."""
        for websocket in websockets.values():
            for event, function, namespace in websocket.events:
                self.register_websocket(event, function, namespace)

    def register_websocket(self, name, function, namespace='/'):
        """Method used to register websocket channel."""
        self.server.on_event(name, function, namespace)

    def register_web_ui(self):
        """Method used to register routes to the admin-ui homepage."""
        self.app.add_url_rule('/', self.web_ui.__name__, self.web_ui)
        self.app.add_url_rule('/index.html', self.web_ui.__name__, self.web_ui)

    @property
    def rest_endpoints(self):
        """Return string with routes registered by Api Server."""
        return [x.rule for x in self.app.url_map.iter_rules()]

    def register_kytos_routes(self):
        """Register initial routes from kytos using ApiServer.

        Initial routes are: ['/kytos/status', '/kytos/shutdown']
        """
        if '/kytos/status/' not in self.rest_endpoints:
            self.app.add_url_rule('/kytos/status/', self.status_api.__name__,
                                  self.status_api, methods=['GET'])

        if '/kytos/shutdown' not in self.rest_endpoints:
            self.app.add_url_rule('/kytos/shutdown',
                                  self.shutdown_api.__name__,
                                  self.shutdown_api, methods=['GET'])

    @staticmethod
    def status_api():
        """Display json with kytos status using the route '/kytos/status'."""
        return '{"response": "running"}', 201

    @staticmethod
    def stop_api_server():
        """Method used to send a shutdown request to stop Api Server."""
        try:
            urlopen('http://127.0.0.1:8181/kytos/shutdown')
        except URLError:
            pass

    def shutdown_api(self):
        """Handle shutdown requests received by Api Server.

        This method must be called by kytos using the method
        stop_api_server, otherwise this request will be ignored.
        """
        allowed_host = ['127.0.0.1:8181', 'localhost:8181']
        if request.host not in allowed_host:
            return "", 403

        self.server.stop()

        return 'Server shutting down...', 200

    def web_ui(self):
        """Method used to serve the index.html page for the admin-ui."""
        return send_from_directory(self.flask_dir, 'index.html')
