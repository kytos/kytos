import sys
import argparse
import textwrap

class KycoCmdLine():
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='PROG',
                        formatter_class=argparse.RawDescriptionHelpFormatter,
                        description=textwrap.dedent('Kytos Controller Daemon.'))

        # TODO: Get version automatically
        self.parser.add_argument('-v', '--version',
                            action='version',
                            version='%(prog)s 0.1.0')

        self.parser.add_argument('-D', '--debug',
                                 action='store_true',
                                 help="Run in debug mode")

        self.parser.add_argument('-d', '--daemon',
                                 action='store_true',
                                 help="Run in daemon mode")

    def parse_args(self):
        self.args = self.parser.parse_args()

#    def execute(self):
#        self.args.func(self.args)
