import logging
import os
import daemon
import lockfile
import signal
import time
import sys

log = logging.getLogger(__name__)

class NoDaemonContext(object):
    """A mock DaemonContext for running kyco without being a daemon."""

    def __init__(self, **kwargs):
        # Do we need pidfile and a different working dir ?
        self.signal_map     = kwargs.pop('signal_map', {})
        self.pidfile        = kwargs.pop('pidfile', None)
        self.working_dir    = kwargs.pop('working_directory', None)

    def __enter__(self):
        for signum, handler in self.signal_map.items():
            signal.signal(signum, handler)

        os.chdir(self.working_dir)
        if self.pidfile:
            self.pidfile.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pidfile:
            self.pidfile.__exit__(exc_type, exc_val, exc_tb)

    def terminate(self, *args):
        print("Terminate requested, without context")
        sys.exit(0)


class KycoDaemon(object):
    """Daemonize and run the kyco daemon."""

    def __init__(self, options):
        self.options    = options
        #context_class   = NoDaemonContext if self.options.nodaemon else daemon.DaemonContext
        context_class   = NoDaemonContext
        self.context    = self._build_context(options, context_class)

    def _build_context(self, options, context_class):
        signal_map = {
            signal.SIGHUP:  self._handle_reconfigure,
            signal.SIGINT:  self._handle_graceful_shutdown,
            signal.SIGTERM: self._handle_shutdown,
        }
        #pidfile = lockfile.FileLock(options.pid_file)
        pidfile = lockfile.FileLock('/var/run/kyco/kyco.pid')
        return context_class(
            #working_directory = options.working_dir,
            working_directory = '/opt/kytos',
            umask = 0o022,
            pidfile = pidfile,
            signal_map = signal_map,
            files_preserve = [pidfile.path]
        )

    def run(self):
        with self.context:
            # setup_logging(self.options)
            while True:
                print(self.context.pidfile)
                time.sleep(2)

    def _handle_shutdown(self, sig_num, stack_frame):
        print("Shutdown requested: sig %s" % sig_num)
        #self.reactor.stop()
        self.context.terminate(sig_num, stack_frame)

    def _handle_graceful_shutdown(self, sig_num, stack_frame):
        """Gracefully shutdown by waiting for Jobs to finish."""
        print("Graceful Shutdown requested: sig %s" % sig_num)
        self.context.terminate(sig_num, stack_frame)
        self._wait_for_jobs()

    def _wait_for_jobs(self):
        """Waiting for jobs"""
        pass

    def _handle_reconfigure(self, _signal_number, _stack_frame):
        """Reconfigure requested by SIGHUP."""
        # asyncio reconfigure task on call later ?
        pass
