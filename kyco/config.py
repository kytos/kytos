"""
Here you can control the config parameters to run kyco controller.

Basically you can use a config file (-c option) and use arguments on command
line. If you specify a config file, then and option configured inside this file
will be overridden by the option on command line.
"""

import sys

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

        parser.add_argument('-p', '--pidfile',
                            action='store_true',
                            help="Specify the PID file to save.")

        parser.add_argument('-w', '--workdir',
                            action='store_true',
                            help="Specify the working directory to use.")

        self.conf_parser, self.parser = conf_parser, parser
        self.parse_args()

    def parse_args(self):
        defaults = {'pidfile': '/var/run/kyco.pid',
                    'workdir': '/var/lib/kyco',
                    'conf': '/etc/kyco/kyco.conf',
                    'logging': '/etc/kyco/logging.ini',
                    'daemon': False,
                    'debug': False}

        args, argv = self.conf_parser.parse_known_args()

        if args.conf:
            config = ConfigParser()
            config.read([args.conf])
            defaults = dict(config.items("daemon"))

        self.parser.set_defaults(**defaults)
        if 'test' in argv:
            argv.pop(argv.index('test'))
        self.args = self.parser.parse_args(argv)
