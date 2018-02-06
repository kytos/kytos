"""Module used to manage kytos processes without or with daemon context."""
from time import sleep

from daemons.prefab import run


class KytosDaemon(run.RunDaemon):  # pylint: disable=too-many-ancestors
    """Class to handle kytos controller in daemon mode."""

    def __init__(self, controller=None):
        """Instance a KytosDaemon.

        Args:
            controller(KytosController): Kytos controller
        """
        self.controller = controller
        super().__init__(pidfile=controller.options.pidfile)

    def run(self):
        """Run the controller and keep alive."""
        try:
            self.controller.start()
        except SystemExit as exception:
            self.controller.log.error(exception)
            self.controller.log.info("Kytos daemon start aborted.")
        while True:
            sleep(0.5)

    def shutdown(self, signum):
        """Stop the controller and shutdown the process."""
        self.controller.stop()
        while True:
            if self.controller.status() == 'Stopped':
                super().shutdown(signum)
            sleep(0.5)
