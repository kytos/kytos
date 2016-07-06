import logging


def start_logger():
    general_formatter = logging.Formatter('%(asctime)s - %(levelname)s - '
                                          '[%(name)s] %(message)s')
    app_formatter = logging.Formatter('%(asctime)s - %(levelname)s - '
                                      '[%(name)s] %(message)s')

    controllerConsoleHandler = logging.StreamHandler()
    controllerConsoleHandler.setLevel(logging.DEBUG)
    controllerConsoleHandler.setFormatter(general_formatter)

    appConsoleHandler = logging.StreamHandler()
    appConsoleHandler.setLevel(logging.DEBUG)
    appConsoleHandler.setFormatter(app_formatter)

    clogger = logging.getLogger('kytos[C]')
    clogger.setLevel(logging.DEBUG)
    clogger.addHandler(controllerConsoleHandler)

    alogger = logging.getLogger('kytos[A]')
    alogger.setLevel(logging.DEBUG)
    alogger.addHandler(appConsoleHandler)

    return clogger
