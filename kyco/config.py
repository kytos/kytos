"""Here you can control the config parameters to run kyco controller.

Basically you can use a config file (-c option) and use arguments on command
line. If you specify a config file, then and option configured inside this file
will be overridden by the option on command line.
"""

import os

from configparser import ConfigParser

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from kyco import __version__

if 'VIRTUAL_ENV' in os.environ:
    BASE_ENV = os.environ['VIRTUAL_ENV']
else:
    BASE_ENV = '/'


class KycoConfig():
    def __init__(self):
        self.options = {}
        conf_parser = ArgumentParser(add_help=False)

        conf_parser.add_argument("-c", "--conf",
                                 help="Specify a config file",
                                 metavar="FILE")

        parser = ArgumentParser(prog='kyco',
                                parents=[conf_parser],
                                formatter_class=RawDescriptionHelpFormatter,
                                description=__doc__)

        parser.add_argument('-v', '--version',
                            action='version',
                            version="kyco %s" % __version__)

        parser.add_argument('-D', '--debug',
                            action='store_true',
                            help="Run in debug mode")

        parser.add_argument('-d', '--daemon',
                            action='store_true',
                            help="Run in daemon mode")

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

        self.conf_parser, self.parser = conf_parser, parser
        self.parse_args()

    def parse_args(self):

        defaults = {'pidfile': os.path.join(BASE_ENV, 'var/run/kyco.pid'),
                    'workdir': os.path.join(BASE_ENV, 'var/lib/kyco'),
                    'napps': os.path.join(BASE_ENV, 'var/lib/kytos/napps/'),
                    'conf': os.path.join(BASE_ENV, 'etc/kyco/kyco.conf'),
                    'logging': os.path.join(BASE_ENV, 'etc/kyco/logging.ini'),
                    'listen': '0.0.0.0',
                    'port': 6633,
                    'daemon': False,
                    'debug': False}

        options, argv = self.conf_parser.parse_known_args()

        if options.conf:
            config = ConfigParser()
            config.read([options.conf])
            defaults = dict(config.items("daemon"))

        self.parser.set_defaults(**defaults)

        if 'test' in argv:
            argv.pop(argv.index('test'))

        self.options['daemon'] = self.parser.parse_args(argv)
