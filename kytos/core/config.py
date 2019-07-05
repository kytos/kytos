"""Here you can control the config parameters to run Kytos controller.

Basically you can use a config file (-c option) and use arguments on command
line. If you specify a config file, then and option configured inside this file
will be overridden by the option on command line.
"""

import json
import os
import warnings
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from configparser import ConfigParser

from kytos.core.metadata import __version__

BASE_ENV = os.environ.get('VIRTUAL_ENV', None) or '/'


class KytosConfig():
    """Handle settings of Kytos."""

    def __init__(self):
        """Parse the command line.

        The contructor set defaults parameters that can be used by KytosConfig.
        """
        self.options = {}
        conf_parser = ArgumentParser(add_help=False)

        conf_parser.add_argument("-c", "--conf",
                                 help="Specify a config file",
                                 metavar="FILE")

        parser = ArgumentParser(prog='kytosd',
                                parents=[conf_parser],
                                formatter_class=RawDescriptionHelpFormatter,
                                description=__doc__)

        parser.add_argument('-v', '--version',
                            action='version',
                            version="kytosd %s" % __version__)

        parser.add_argument('-D', '--debug',
                            action='store_true',
                            help="Run in debug mode")

        parser.add_argument('-f', '--foreground',
                            action='store_true',
                            help="Run in foreground (ctrl+c to stop)")

        parser.add_argument('-l', '--listen',
                            action='store',
                            help="IP/Interface to be listened")

        parser.add_argument('-n', '--napps',
                            action='store',
                            help="Specify the napps directory")

        parser.add_argument('-P', '--port',
                            action='store',
                            help="Port to be listened")

        parser.add_argument('-p', '--pidfile',
                            action='store',
                            help="Specify the PID file to save.")

        parser.add_argument('-w', '--workdir',
                            action='store',
                            help="Specify the working directory")

        parser.add_argument('-s', '--protocol_name',
                            action='store',
                            help="Specify the southbound protocol")

        parser.add_argument('-E', '--enable_entities_by_default',
                            action='store_true',
                            help="Enable all new Entities by default.")

        self.conf_parser, self.parser = conf_parser, parser
        self.parse_args()

    def parse_args(self):
        """Get the command line options and update kytos settings.

        When installed via pip, defaults values are:

        .. code-block:: python

            defaults = {'pidfile': '/var/run/kytos/kytosd.pid',
                        'workdir': '/var/lib/kytos',
                        'napps': '/var/lib/kytos/napps/',
                        'conf': '/etc/kytos/kytos.conf',
                        'logging': '/etc/kytos/logging.ini',
                        'listen': '0.0.0.0',
                        'port': 6653,
                        'foreground': False,
                        'protocol_name': '',
                        'enable_entities_by_default': False,
                        'debug': False}

        """
        defaults = {'pidfile': os.path.join(BASE_ENV,
                                            'var/run/kytos/kytosd.pid'),
                    'workdir': os.path.join(BASE_ENV, 'var/lib/kytos'),
                    'napps': os.path.join(BASE_ENV, 'var/lib/kytos/napps/'),
                    'napps_repositories': "['https://napps.kytos.io/repo/']",
                    'installed_napps': os.path.join(BASE_ENV,
                                                    'var/lib/kytos/napps/',
                                                    '.installed'),
                    'conf': os.path.join(BASE_ENV, 'etc/kytos/kytos.conf'),
                    'logging': os.path.join(BASE_ENV, 'etc/kytos/logging.ini'),
                    'listen': '0.0.0.0',
                    'port': 6653,
                    'foreground': False,
                    'protocol_name': '',
                    'enable_entities_by_default': False,
                    'napps_pre_installed': [],
                    'vlan_pool': {},
                    'debug': False}

        options, argv = self.conf_parser.parse_known_args()

        config = ConfigParser()
        result = config.read([options.conf or defaults.get('conf')])

        if result:
            defaults.update(dict(config.items("daemon")))
        else:
            print('There is no config file.')
            exit(-1)

        self.parser.set_defaults(**defaults)

        self.options['daemon'] = self._parse_options(argv)

    def _parse_options(self, argv):
        """Create a Namespace using the given argv.

        Args:
            argv(dict): Python Dict used to create the namespace.

        Returns:
            options(Namespace): Namespace with the args given

        """
        options, unknown = self.parser.parse_known_args(argv)
        if unknown:
            warnings.warn(f"Unknown arguments: {unknown}")
        options.napps_repositories = json.loads(options.napps_repositories)
        options.debug = True if options.debug in ['True', True] else False
        options.daemon = True if options.daemon in ['True', True] else False
        options.port = int(options.port)
        options.api_port = int(options.api_port)
        options.protocol_name = str(options.protocol_name)

        result = options.enable_entities_by_default in ['True', True]
        options.enable_entities_by_default = result

        if isinstance(options.napps_pre_installed, str):
            napps = options.napps_pre_installed
            options.napps_pre_installed = json.loads(napps)

        return options
