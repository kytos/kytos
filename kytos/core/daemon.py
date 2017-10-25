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

    def execute(self, args=None):
        """Execute the daemon based on args given.

        The KytosDaemon will run the first command allowed and ignore the
        others. The allowed commands are: start, stop and status.
        """
        func = self.start
        for command in ['start', 'stop', 'status']:
            if args and command in args:
                func = getattr(self, command)
                break

        if func.__name__ == 'status':
            print(func())
        else:
            func()

    def status(self):
        """Return the KytosController status."""
        try:
            pidfile = open(self.controller.options.pidfile)
            pid = pidfile.readline().strip()
            result = f"The process is already running with pid {pid}."
        except FileNotFoundError:
            result = "Stopped."
        return result

    def shutdown(self, signum):
        """Stop the controller and shutdown the process."""
        self.controller.stop()
        while True:
            if self.controller.status() == 'Stopped':
                super().shutdown(signum)
            sleep(0.5)
