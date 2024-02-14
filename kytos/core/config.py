"""Here you can control the config parameters to run Kytos controller.

Basically you can use a config file (-c option) and use arguments on command
line. If you specify a config file, then and option configured inside this file
will be overridden by the option on command line.
"""

import json
import os
import uuid
import warnings
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from configparser import ConfigParser
from pathlib import Path

from jinja2 import Template

from kytos.core.metadata import __version__

BASE_ENV = os.environ.get('VIRTUAL_ENV', None) or '/'
ETC_KYTOS = 'etc/kytos'
TEMPLATE_FILES = ['templates/kytos.conf.template',
                  'templates/logging.ini.template']
SYSLOG_ARGS = ['/dev/log'] if Path('/dev/log').exists() else []


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
                            version=f"kytosd {__version__}")

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

        parser.add_argument('-C', '--create-superuser',
                            action='store_true',
                            help="Create a kytos superuser.")

        parser.add_argument('-t', '--thread_pool_max_workers',
                            action='store',
                            help="Maximum number of threads in the pool.")

        parser.add_argument('-d', '--database',
                            action='store',
                            help="Database backend.")

        parser.add_argument('-a', '--apm',
                            action='store',
                            help="APM backend.")

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
                        'token_expiration_minutes': 180,
                        'thread_pool_max_workers': 256,
                        'debug': False}

        """
        defaults = {
            'pidfile': os.path.join(
                BASE_ENV,
                'var/run/kytos/kytosd.pid'
            ),
            'workdir': os.path.join(
                BASE_ENV,
                'var/lib/kytos'
            ),
            'napps': os.path.join(
                BASE_ENV,
                'var/lib/kytos/napps/'
            ),
            'napps_repositories': ['https://napps.kytos.io/repo/'],
            'installed_napps': os.path.join(
                BASE_ENV,
                'var/lib/kytos/napps/',
                '.installed'
            ),
            'conf': os.path.join(
                BASE_ENV,
                'etc/kytos/kytos.conf'
            ),
            'logging': os.path.join(
                BASE_ENV,
                'etc/kytos/logging.ini'
            ),
            'logger_decorators': [
                "kytos.core.logger_decorators.queue_decorator",
            ],
            'listen': '0.0.0.0',
            'port': 6653,
            'api_traceback_on_500': True,
            'api_concurrency_limit': 'threadpool',
            'foreground': False,
            'protocol_name': '',
            'enable_entities_by_default': False,
            'napps_pre_installed': [],
            'authenticate_urls': [],
            'token_expiration_minutes': 180,
            'thread_pool_max_workers': {},
            'database': '',
            'apm': '',
            'connection_timeout': 130,
            'debug': False,
            "event_buffer_conf": {
                "msg_out": {
                    "queue": {
                        "type": "priority",
                        "maxsize": "threadpool_sb",
                        "maxsize_multiplier": 2,
                    }
                },
                "msg_in": {
                    "queue": {
                        "type": "priority",
                        "maxsize": "threadpool_sb",
                        "maxsize_multiplier": 2,
                    }
                },
                "raw": {
                    "queue": {
                        "type": "queue",
                        "maxsize": "threadpool_sb",
                        "maxsize_multiplier": 2,
                    }
                },
                "app": {
                    "queue": {
                        "type": "queue",
                        "maxsize": "threadpool_app",
                        "maxsize_multiplier": 2,
                    }
                },
            },
            "thread_pool_queue_monitors": [
              {
                "min_hits": 5,
                "delta_secs": 5,
                "min_queue_full_percent": 150,
                "log_at_most_n": 0,
                "queues": ["sb", "app", "db"]
              }
            ],
            "event_buffer_monitors": [
              {
                "min_hits": 5,
                "delta_secs": 5,
                "min_queue_full_percent": 100,
                "log_at_most_n": 0,
                "buffers": ["msg_in", "msg_out", "raw", "app"]
              }
            ]
        }

        options, argv = self.conf_parser.parse_known_args()

        config = ConfigParser()

        config_file = options.conf or defaults.get('conf')

        if not os.path.exists(config_file):
            _render_config_templates(TEMPLATE_FILES, BASE_ENV,
                                     prefix=BASE_ENV,
                                     syslog_args=SYSLOG_ARGS)

        config.read(config_file)

        defaults.update(dict(config.items("daemon")))

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
        options.debug = options.debug in ['True', True]
        options.daemon = options.daemon in ['True', True]
        options.port = int(options.port)
        options.api_port = int(options.api_port)
        options.api_traceback_on_500 = options.api_traceback_on_500 in ['True',
                                                                        True]
        options.protocol_name = str(options.protocol_name)
        options.token_expiration_minutes = int(options.
                                               token_expiration_minutes)
        result = options.enable_entities_by_default in ['True', True]
        options.enable_entities_by_default = result

        def _parse_json(value):
            """Parse JSON lists and dicts from the config file."""
            if isinstance(value, str):
                return json.loads(value)
            return value

        options.napps_repositories = _parse_json(options.napps_repositories)
        options.logger_decorators = _parse_json(options.logger_decorators)
        options.napps_pre_installed = _parse_json(options.napps_pre_installed)
        options.authenticate_urls = _parse_json(options.authenticate_urls)
        options.thread_pool_max_workers = _parse_json(
            options.thread_pool_max_workers
        )
        options.event_buffer_conf = _parse_json(
            options.event_buffer_conf
        )
        options.event_buffer_monitors = _parse_json(
            options.event_buffer_monitors
        )
        options.thread_pool_queue_monitors = _parse_json(
            options.thread_pool_queue_monitors
        )
        options.api_concurrency_limit = _parse_json(
            options.api_concurrency_limit
        )

        return options

    @staticmethod
    def options_exposed(daemon_options: dict) -> dict:
        """Options exposed on API."""
        options = dict(daemon_options)
        for key in ["jwt_secret"]:
            options.pop(key, None)
        return options


def _render_config_templates(templates,
                             destination=Path(__file__).parent,
                             **kwargs):
    """Create a config file based on a template file.

    If no destination is passed, the new conf file will be created on the
    directory of the template file.

    Args:
        template (string):    Path of the template file
        destination (string): Directory in which the config file will
                              be placed.
    """
    if str(kwargs['prefix']) != '/':
        kwargs['prefix'] = Path(str(kwargs['prefix']).rstrip('/'))
    kwargs['jwt_secret'] = uuid.uuid4().hex

    # Create the paths used by Kytos.
    directories = [os.path.join(BASE_ENV, ETC_KYTOS)]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    tmpl_path = Path(os.path.abspath(os.path.dirname(__file__))).parent

    for tmpl in templates:
        path = os.path.join(tmpl_path, tmpl)
        with open(path, 'r', encoding='utf-8') as src_file:
            content = Template(src_file.read()).render(**kwargs)
            tmpl = tmpl.replace('templates', ETC_KYTOS) \
                       .replace('.template', '')
            dst_path = Path(destination) / tmpl
            with open(dst_path, 'w', encoding="utf8") as dst_file:
                dst_file.write(content)
