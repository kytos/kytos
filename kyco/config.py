"""Here you can control the config parameters to run kyco controller.

Basically you can use a config file (-c option) and use arguments on command
line. If you specify a config file, then and option configured inside this file
will be overridden by the option on command line.
"""

import os
import re

from configparser import ConfigParser

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter


class KycoConfig():
    def __init__(self):
        conf_parser = ArgumentParser(add_help=False)

        conf_parser.add_argument("-c", "--conf",
                                 help="Specify a config file",
                                 metavar="FILE")

        parser = ArgumentParser(prog='kyco',
                                parents=[conf_parser],
                                formatter_class=RawDescriptionHelpFormatter,
                                description=__doc__)

        # TODO: Get version automatically
        parser.add_argument('-v', '--version',
                            action='version',
                            version='%(prog)s 0.1.0')

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
        napps = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                             'napps')

        defaults = {'pidfile': '/var/run/kyco.pid',
                    'workdir': '/var/lib/kyco',
                    'napps': napps,
                    'conf': '/etc/kyco/kyco.conf',
                    'logging': '/etc/kyco/logging.ini',
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
        for item in argv:
            # Check if we are running a single unittest directly
            # python -m unittest tests.<something>
            # Config from the command line, so we can just ignore all argvs.
            if re.match('tests\..*', item):
                argv.clear()
                break
            # In this case we are running the full test suite with
            # python setup.py test
            # Then we are just going to ignore this CLI argument, it was not
            # intended to be used on Config, but on the setup call.
            if re.match('test', item):
                argv.remove(item)
        self.options = self.parser.parse_args(argv)
