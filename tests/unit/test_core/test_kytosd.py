"""Test kytos.core.kytosd module."""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from kytos.core.kytosd import _create_pid_dir, async_main, create_shell, main


class TestKytosd(TestCase):
    """Kytosd tests."""

    @staticmethod
    @patch('os.makedirs')
    @patch('kytos.core.kytosd.BASE_ENV', '/tmp/')
    def test_create_pid_dir__env(mock_mkdirs):
        """Test _create_pid_dir method with env."""
        _create_pid_dir()

        mock_mkdirs.assert_called_with('/tmp/var/run/kytos', exist_ok=True)

    @staticmethod
    @patch('os.chmod')
    @patch('os.makedirs')
    @patch('kytos.core.kytosd.BASE_ENV', '/')
    def test_create_pid_dir__system(*args):
        """Test _create_pid_dir method with system dir."""
        (mock_mkdirs, mock_chmod) = args
        _create_pid_dir()

        mock_mkdirs.assert_called_with('/var/run/kytos', exist_ok=True)
        mock_chmod.assert_called_with('/var/run/kytos', 0o1777)

    @staticmethod
    @patch('kytos.core.kytosd.InteractiveShellEmbed')
    def test_start_shell(mock_interactive_shell):
        """Test stop_api_server method."""
        ipshell = create_shell(MagicMock())
        ipshell()

        mock_interactive_shell.assert_called()

    @staticmethod
    @patch('kytos.core.kytosd.async_main')
    @patch('kytos.core.kytosd._create_pid_dir')
    @patch('kytos.core.kytosd.KytosConfig')
    def test_main__foreground(*args):
        """Test main method in foreground."""
        (mock_kytos_config, mock_create_pid_dir, mock_async_main) = args
        config = MagicMock(foreground=True)
        options = {'daemon': config}
        mock_kytos_config.return_value.options = options

        main()

        mock_create_pid_dir.assert_called()
        mock_async_main.assert_called()

    @staticmethod
    @patch('kytos.core.kytosd.daemon.DaemonContext')
    @patch('kytos.core.kytosd.async_main')
    @patch('kytos.core.kytosd._create_pid_dir')
    @patch('kytos.core.kytosd.KytosConfig')
    def test_main__background(*args):
        """Test main method in background."""
        (mock_kytos_config, mock_create_pid_dir, mock_async_main, _) = args
        config = MagicMock(foreground=False)
        options = {'daemon': config}
        mock_kytos_config.return_value.options = options

        main()

        mock_create_pid_dir.assert_called()
        mock_async_main.assert_called()

    @staticmethod
    @patch('kytos.core.kytosd.asyncio')
    @patch('kytos.core.kytosd.InteractiveShellEmbed')
    @patch('kytos.core.kytosd.Controller')
    def test_async_main(*args):
        """Test async_main method."""
        (mock_controller, _, mock_asyncio) = args
        controller = MagicMock()
        controller.options.debug = True
        controller.options.foreground = True
        mock_controller.return_value = controller

        event_loop = MagicMock()
        mock_asyncio.get_event_loop.return_value = event_loop

        async_main(MagicMock())

        event_loop.call_soon.assert_called_with(controller.start)
