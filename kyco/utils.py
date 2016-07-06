"""Utilities"""

import logging

APP_MSG = "[App %s] %s | ID: %02d | R: %02d | P: %02d | F: %s"


def start_logger():
    general_formatter = logging.Formatter('%(asctime)s - %(levelname)s '
                                          '[%(name)s] %(message)s')
    app_formatter = logging.Formatter('%(asctime)s - %(levelname)s '
                                      '[%(name)s] %(message)s')

    controller_console_handler = logging.StreamHandler()
    controller_console_handler.setLevel(logging.DEBUG)
    controller_console_handler.setFormatter(general_formatter)

    app_console_handler = logging.StreamHandler()
    app_console_handler.setLevel(logging.DEBUG)
    app_console_handler.setFormatter(app_formatter)

    controller_log = logging.getLogger('Kyco')
    controller_log.setLevel(logging.DEBUG)
    controller_log.addHandler(controller_console_handler)

    app_log = logging.getLogger('KycoNApp')
    app_log.setLevel(logging.DEBUG)
    app_log.addHandler(app_console_handler)

    return controller_log
