from flask import Flask, request
from flask_socketio import SocketIO


class APIServer:

    def __init__(self, app_name):
        self.app = Flask(app_name)
        self.server = SocketIO(self.app)

    def run(self, *args, **kwargs ):
        self.server.run(self.app, *args, **kwargs)

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

    @property
    def rest_endpoints(self):
        """Return string with routes registered by Api Server."""
        return [x.rule for x in self.app.url_map.iter_rules()]

    def register_kyco_routes(self):
        """Register initial routes from kyco using ApiServer.

        Initial routes are: ['/kytos/status', '/kytos/shutdown']
        """
        if '/kytos/status/' not in self.rest_endpoints:
            self.app.add_url_rule('/kytos/status/', self.status_api.__name__,
                                  self.status_api, methods=['GET'])

        if '/kytos/shutdown' not in self.rest_endpoints:
            self.app.add_url_rule('/kytos/shutdown',
                                  self.shutdown_api.__name__,
                                  self.shutdown_api, methods=['GET'])

    def shutdown_api(self):
        """Handle shutdown requests received by Api Server.

        This method must be called by kyco using the method
        stop_api_server, otherwise this request will be ignored.
        """
        allowed_host = ['127.0.0.1:8181', 'localhost:8181']
        if request.host not in allowed_host:
            return "", 403

        server_shutdown = request.environ.get('werkzeug.server.shutdown')
        if server_shutdown is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        server_shutdown()
        return 'Server shutting down...', 200

    def status_api(self):
        """Display json with kyco status using the route '/status'."""
        return '{"response": "running"}', 201
