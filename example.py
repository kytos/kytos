import os
from configparser import ConfigParser

from kyco.controller import Controller


if __name__ == '__main__':
    config = ConfigParser()
    config.read('kyco_config.ini')

    HOST = config.get('TCP', 'HOST')
    PORT = config.getint('TCP', 'PORT')
    NAPPS_DIR = os.path.join(os.getcwd(), 'apps')
    controller = Controller()
    controller.start()
