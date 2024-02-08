"""Test the decorators for the loggers"""
from logging.handlers import QueueHandler
from unittest.mock import MagicMock, Mock, patch

from kytos.core.logger_decorators import (apm_decorator, queue_decorator,
                                          root_decorator)


class DummyLoggerClass:
    """Dummy class for testing decorating"""
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.parent = None
        self.propagate = True
        self.handlers = []
        self.filters = []

    # pylint: disable=invalid-name
    def addHandler(self, hdlr):
        """Add in handler."""
        if hdlr not in self.handlers:
            self.handlers.append(hdlr)

    def hasHandlers(self):
        """Check if has handlers"""
        if self.handlers:
            return True
        return False
    # pylint: enable=invalid-name


for method_name in ['debug', 'info', 'warning', 'error',
                    'exception', 'critical', 'fatal', 'log']:
    setattr(DummyLoggerClass, method_name,
            MagicMock(__name__=method_name, __module__='logging'))


class TestRootDecorator:
    """Test the root logger decorator"""

    def setup_method(self):
        """Create decorated class for tests"""
        self.decorated_class = root_decorator(DummyLoggerClass)

    def test_init_logger(self):
        """Test class initialization"""
        level = 5
        logger = self.decorated_class(level)
        assert logger.name == 'root'
        assert logger.level == level


class TestQueueDecorator:
    """Test the queue logger decorator"""

    def setup_method(self):
        """Create decorated class for tests"""
        self.decorated_class = queue_decorator(DummyLoggerClass)

    def test_init_logger(self):
        """Test class initialization"""
        name = 'test'
        level = 4
        logger = self.decorated_class(name, level)
        assert logger.name == name
        assert logger.level == level
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], QueueHandler)
        assert not logger.hasHandlers()

    def test_add_remove_handler(self):
        """Test adding and removing handlers"""
        name = 'test'
        level = 4
        logger = self.decorated_class(name, level)
        handler_mock = Mock()
        # Add 1 handler then remove
        logger.addHandler(handler_mock)
        assert logger.hasHandlers()
        assert len(logger.handlers) == 1
        logger.removeHandler(handler_mock)
        assert not logger.hasHandlers()
        assert len(logger.handlers) == 1

        # Add 1 handler twice, then remove
        logger.addHandler(handler_mock)
        logger.addHandler(handler_mock)
        assert logger.hasHandlers()
        logger.removeHandler(handler_mock)
        assert not logger.hasHandlers()


class TestAPMDecorator:
    """Test the APM logger decorator"""

    def setup_method(self):
        """Create decorated class for tests"""
        self.decorated_class = apm_decorator(DummyLoggerClass)

    @patch('kytos.core.apm.execution_context')
    def test_decorated_logger(self, mock_context):
        """Test the decorated logger."""

        transaction = MagicMock()

        mock_context.get_transaction.return_value = transaction

        name = 'test'
        level = 3
        logger = self.decorated_class(name, level)
        assert logger.name == name
        assert logger.level == level

        log_module = 'logging'
        log_methods = ['debug', 'info', 'warning', 'error',
                       'exception', 'critical', 'fatal', 'log']
        span_type = 'logging'

        for meth_name in log_methods:
            # Setup Mocks
            base_mock_method = getattr(DummyLoggerClass, meth_name)
            transaction.begin_span = MagicMock()
            transaction.end_span = MagicMock()

            # Construct args
            msg = f'Logging with {meth_name}'
            if meth_name == 'log':
                args = [6, msg]
            else:
                args = [msg]
            method = getattr(logger, meth_name)

            # Call
            method(*args)

            # Test Conditions
            transaction.begin_span \
                       .assert_called_with(f'{log_module}.{meth_name}',
                                           span_type)
            base_mock_method.assert_called_with(logger, *args)
            transaction.end_span.assert_called()
