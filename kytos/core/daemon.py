"""Module used to manage kytos processes without or with daemon context."""
# import logging
# import os
# import signal
# import sys
# import time
#
# from daemon import DaemonContext
# from daemon.pidfile import PIDLockFile
#
# log = logging.getLogger(__name__)
#
#
# class NoDaemonContext(object):
#     """A mock DaemonContext for running kytos without being a daemon."""
#
#     def __init__(self, **kwargs):
#         """Constructor of NoDaemonContext receive the parameters below.
#
#         Parameters:
#             signal_map (dict): dictionary with signals used in kytos.
#             pidfile (string): address of a pidfile to be used in kytos.
#             working_dir (string): working directory to be used in kytos.
#         """
#         # Do we need pidfile and a different working dir ?
#         self.signal_map = kwargs.pop('signal_map', {})
#         self.pidfile = kwargs.pop('pidfile', None)
#         self.working_dir = kwargs.pop('working_directory', None)
#
#     def __enter__(self):
#         """Signals, working directory and pidfile are built."""
#         for signum, handler in self.signal_map.items():
#             signal.signal(signum, handler)
#
#         os.chdir(self.working_dir)
#         if self.pidfile:
#             self.pidfile.__enter__()
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         """Pidfile will be closed."""
#         if self.pidfile:
#             self.pidfile.__exit__(exc_type, exc_val, exc_tb)
#
#     def terminate(self, *args):
#         """Method used to shutdown the kytosd process."""
#         print("Terminate requested, without context")
#         sys.exit(0)
#
#
# class KytosDaemon(object):
#     """Daemonize and run the kytos daemon."""
#
#     def __init__(self, options):
#         """Constructor of KytosDaemon service the parameters below.
#
#         Parameters
#             options (dict): python dictionary with options to run kytos.
#         """
#         self.options = options
#         context_class = DaemonContext if options.daemon else NoDaemonContext
#         self.context = self._build_context(options, context_class)
#
#     def _build_context(self, options, context_class):
#         signal_map = {
#             signal.SIGHUP:  self._handle_reconfigure,
#             signal.SIGINT:  self._handle_graceful_shutdown,
#             signal.SIGTERM: self._handle_shutdown,
#         }
#         pidfile = PIDLockFile(self.options.pidfile)
#         return context_class(
#             working_directory=self.options.workdir,
#             umask=0x022,
#             pidfile=pidfile,
#             signal_map=signal_map,
#             files_preserve=[pidfile.path])
#
#     def run(self):
#         """Method used to hold kytos processes."""
#         # setup_logging(self.options)
#         # We should print nice message if daemon is_open.
#         with self.context:
#             while True:
#                 print(self.context)
#                 time.sleep(2)
#
#     def _handle_shutdown(self, sig_num, stack_frame):
#         print("Shutdown requested: sig %s" % sig_num)
#         # self.reactor.stop()
#         self.context.terminate(sig_num, stack_frame)
#
#     def _handle_graceful_shutdown(self, sig_num, stack_frame):
#         """Gracefully shutdown by waiting for Jobs to finish."""
#         print("Graceful Shutdown requested: sig %s" % sig_num)
#         self.context.terminate(sig_num, stack_frame)
#         self._wait_for_jobs()
#
#     def _wait_for_jobs(self):
#         """Waiting for jobs."""
#         pass
#
#     def _handle_reconfigure(self, _signal_number, _stack_frame):
#         """Reconfigure requested by SIGHUP."""
#         # asyncio reconfigure task on call later ?
#         pass
