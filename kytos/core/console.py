"""Module to Handle KytosConsole"""
import IPython
import signal
import sys
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.prompts import Prompts, Token
from traitlets.config.loader import Config
from kytos.core.constants import BANNER, EXIT_MSG

class KytosPrompt(Prompts):
     def in_prompt_tokens(self, cli=None):
         return [(Token.Prompt, 'kytos $> ')]

class KytosConsole:

    controller = None
    kill_signals = (
        2,  # SIGINT
        3,  # SIGQUIT
        6,  # SIGABRT
        15, # SIGTERM
    )

    def __init__(self, controller=None):
        """Start the console using a controller given."""
        self.controller = controller
        self.banner = BANNER
        self.exit_msg = EXIT_MSG
        self._start_handlers()

    def _improve_banner(self):
        """Improve the banner using the controller attributes."""
        address = self.controller.server.server_address[0]
        port = self.controller.server.server_address[1]
        self.banner += " tcp://{}:{}\n".format(address, port)

        api_port = self.controller.api_server.port
        self.banner += "WEB UI........: http://{}:{}/".format(address,
                                                              api_port)

    def _create_shell(self):
        """Create an Iterative Shell"""
        cfg = Config()
        cfg.TerminalInteractiveShell.autocall = 2
        cfg.TerminalInteractiveShell.show_rewritten_input = False

        self.ipshell = InteractiveShellEmbed(config=cfg,
                                        banner1=self.banner,
                                        exit_msg=self.exit_msg)
        self.ipshell.prompts = KytosPrompt(self.ipshell)

    def start(self):
        """Start the controller and run the python console."""
        try:
            self.controller.start()
        except SystemExit as e:
            self.controller.log.error(e)
            self.controller.log.info("Kytos start aborted.")
            sys.exit()

        self._improve_banner()
        self._create_shell()
        self.ipshell()
        self.shutdown()

    def shutdown(self):
        """Stop the controller before quitting."""
        if self.controller:
            self.controller.stop()

    def _handle_signals(self, signum, frame):
        """Handle signals received."""
        if signum in self.kill_signals:
            self.shutdown()
        sys.exit()

    def _start_handlers(self):
        """Register private method _handle_signal to handle kill signals."""
        for signum in self.kill_signals:
            signal.signal(signum, self._handle_signals)
