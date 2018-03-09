#!/usr/bin/env python3.6
"""Start Kytos SDN Platform core."""
import signal
import sys

import daemon
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.prompts import Prompts, Token
from traitlets.config.loader import Config

from kytos.core import Controller
from kytos.core.config import KytosConfig


class KytosPrompt(Prompts):
    """Configure Kytos prompt for interactive shell."""

    def in_prompt_tokens(self, cli=None):
        """Kytos IPython prompt."""
        return [(Token.Prompt, 'kytos $> ')]


def start_shell(controller):
    """Load Kytos interactive shell."""
    # pylint: disable=anomalous-backslash-in-string
    banner1 = """\033[95m
      _          _
     | |        | |
     | | ___   _| |_ ___  ___
     | |/ / | | | __/ _ \/ __|
     |   <| |_| | || (_) \__ \\
     |_|\_\\\\__, |\__\___/|___/
            __/ |
           |___/
    \033[0m
    Welcome to Kytos SDN Platform!

    We are doing a huge effort to make sure that this console will work fine
    but for now it's still experimental.

    Kytos website.: https://kytos.io/
    Documentation.: https://docs.kytos.io/
    OF Address....:"""

    exit_msg = "Stopping Kytos daemon... Bye, see you!"

    address = controller.server.server_address[0]
    port = controller.server.server_address[1]
    banner1 += " tcp://{}:{}\n".format(address, port)

    api_port = controller.api_server.port
    banner1 += "    WEB UI........: http://{}:{}/".format(address, api_port)

    cfg = Config()
    cfg.TerminalInteractiveShell.autocall = 2
    cfg.TerminalInteractiveShell.show_rewritten_input = False

    ipshell = InteractiveShellEmbed(config=cfg,
                                    banner1=banner1,
                                    exit_msg=exit_msg)
    ipshell.prompts = KytosPrompt(ipshell)

    ipshell()


def main():
    """Start main Kytos Daemon."""
    def stop_controller(signum, frame):     # pylint: disable=unused-argument
        """Stop the controller before quitting."""
        if controller:
            print('Stopping controller...')
            # If stop() hangs, old ctrl+c behaviour will be restored
            signal.signal(signal.SIGINT, kill_handler)
            controller.stop()

    kill_handler = signal.signal(signal.SIGINT, stop_controller)

    config = KytosConfig()
    controller = Controller(config.options['daemon'])

    if controller.options.foreground:
        try:
            controller.start()
        except SystemExit as exc:
            controller.log.error(exc)
            controller.log.info("Kytos start aborted.")
            sys.exit()

        start_shell(controller)

        controller.stop()
    else:
        with daemon.DaemonContext():
            try:
                controller.start()
            except SystemExit as exc:
                controller.log.error(exc)
                controller.log.info("Kytos daemon start aborted.")
                sys.exit()
