#!/usr/bin/env python3.6
"""Start Kytos SDN Platform core."""
import asyncio
import functools
import os
import signal
import logging
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import daemon
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.prompts import Prompts, Token
from traitlets.config.loader import Config
from kytos.core import Controller
from kytos.core.config import KytosConfig
from kytos.core.metadata import __version__

BASE_ENV = Path(os.environ.get('VIRTUAL_ENV', '/'))


class KytosPrompt(Prompts):
    """Configure Kytos prompt for interactive shell."""

    def in_prompt_tokens(self):
        """Kytos IPython prompt."""
        return [(Token.Prompt, 'kytos $> ')]


def _create_pid_dir():
    """Create the directory in /var/run to hold the pidfile."""
    pid_dir = os.path.join(BASE_ENV, 'var/run/kytos')
    os.makedirs(pid_dir, exist_ok=True)
    if BASE_ENV == '/':  # system install
        os.chmod(pid_dir, 0o1777)  # permissions like /tmp


def start_shell(controller=None):
    """Load Kytos interactive shell."""
    kytos_ascii = r"""
      _          _
     | |        | |
     | | ___   _| |_ ___  ___
     | |/ / | | | __/ _ \/ __|
     |   <| |_| | || (_) \__ \
     |_|\_\__,  |\__\___/|___/
            __/ |
           |___/
    """

    banner1 = f"""\033[95m{kytos_ascii}\033[0m
    Welcome to Kytos SDN Platform!

    We are making a huge effort to make sure that this console will work fine
    but for now it's still experimental.

    Kytos website.: https://kytos.io/
    Documentation.: https://docs.kytos.io/
    OF Address....:"""

    exit_msg = "Stopping Kytos daemon... Bye, see you!"

    if controller:
        address = controller.server.server_address[0]
        port = controller.server.server_address[1]
        banner1 += f" tcp://{address}:{port}\n"

        api_port = controller.api_server.port
        banner1 += f"    WEB UI........: http://{address}:{api_port}/\n"
        banner1 += f"    Kytos Version.: {__version__}"

    banner1 += "\n"

    cfg = Config()
    cfg.TerminalInteractiveShell.autocall = 2
    cfg.TerminalInteractiveShell.show_rewritten_input = False
    cfg.TerminalInteractiveShell.confirm_exit = False

    # Avoiding sqlite3.ProgrammingError when trying to save command history
    # on Kytos shutdown
    cfg.HistoryAccessor.enabled = False

    ipshell = InteractiveShellEmbed(config=cfg,
                                    banner1=banner1,
                                    exit_msg=exit_msg)
    ipshell.prompts = KytosPrompt(ipshell)

    ipshell()


# def disable_threadpool_exit():
#     """Avoid traceback when ThreadPool tries to shut down threads again."""
#     import atexit
#     from concurrent.futures import thread, ThreadPoolExecutor
#     atexit.unregister(thread._python_exit)

def main():
    """Read config and start Kytos in foreground or daemon mode."""
    # data_files is not enough when installing from PyPI

    _create_pid_dir()

    config = KytosConfig().options['daemon']

    # Configure to log uncaught exceptions to errlog file
    sys.excepthook = exhandler

    if config.foreground:
        async_main(config)
    else:
        with daemon.DaemonContext():
            async_main(config)


def exhandler(exctype, value, traceback):
    """Define exception hook hanndler
        
        Args:
            exctype: exception type
            value: value of exception
            tb: traceback
    """
    #
    # logs uncaught exceptions into the console and errlog.log
    traceback.print_exception(exctype, value, traceback)
    print(traceback)
    # pylint: disable=logging-format-interpolation
    logging.basicConfig(filename='kytos/kytos/core/errlog.log',
                        format='%(asctime)s:%(pathname)s:'
                        '%(levelname)s:%(message)s')
    logging.exception('Uncaught Exception: {0}'.format(str(value)))
    print('Uncaught Exception: {0}'.format(str(value)))


def async_main(config):
    """Start main Kytos Daemon with asyncio loop."""
    def stop_controller(controller):
        """Stop the controller before quitting."""
        loop = asyncio.get_event_loop()

        # If stop() hangs, old ctrl+c behaviour will be restored
        loop.remove_signal_handler(signal.SIGINT)
        loop.remove_signal_handler(signal.SIGTERM)

        # disable_threadpool_exit()

        controller.log.info("Stopping Kytos controller...")
        controller.stop()

    async def start_shell_async():
        """Run the shell inside a thread and stop controller when done."""
        _start_shell = functools.partial(start_shell, controller)
        data = await loop.run_in_executor(executor, _start_shell)
        executor.shutdown()
        stop_controller(controller)
        return data

    loop = asyncio.get_event_loop()

    controller = Controller(config)

    kill_handler = functools.partial(stop_controller, controller)
    loop.add_signal_handler(signal.SIGINT, kill_handler)
    loop.add_signal_handler(signal.SIGTERM, kill_handler)

    if controller.options.debug:
        loop.set_debug(True)

    loop.call_soon(controller.start)

    if controller.options.foreground:
        executor = ThreadPoolExecutor(max_workers=1)
        loop.create_task(start_shell_async())

    try:
        loop.run_forever()
    except SystemExit as exc:
        controller.log.error(exc)
        controller.log.info("Shutting down Kytos...")
    finally:
        loop.close()
