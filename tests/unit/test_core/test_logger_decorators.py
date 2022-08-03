"""Test the decorators for the loggers"""
from logging.handlers import QueueHandler
from unittest import TestCase
from unittest.mock import Mock

from kytos.core.logger_decorators import queue_decorator, root_decorator


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


class RootDecoratorTest(TestCase):
    """Test the root logger decorator"""

    def setUp(self):
        """Create decorated class for tests"""
        self.decorated_class = root_decorator(DummyLoggerClass)

    def test_init_logger(self):
        """Test class initialization"""
        level = 5
        logger = self.decorated_class(level)
        self.assertEqual(logger.name, 'root')
        self.assertEqual(logger.level, level)

    def tearDown(self):
        pass


class QueueDecoratorTest(TestCase):
    """Test the queue logger decorator"""

    def setUp(self):
        """Create decorated class for tests"""
        self.decorated_class = queue_decorator(DummyLoggerClass)

    def test_init_logger(self):
        """Test class initialization"""
        name = 'test'
        level = 4
        logger = self.decorated_class(name, level)
        self.assertEqual(logger.name, name)
        self.assertEqual(logger.level, level)
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], QueueHandler)
        self.assertFalse(logger.hasHandlers())

    def test_add_remove_handler(self):
        """Test adding and removing handlers"""
        name = 'test'
        level = 4
        logger = self.decorated_class(name, level)
        handler_mock = Mock()
        # Add 1 handler then remove
        logger.addHandler(handler_mock)
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)
        logger.removeHandler(handler_mock)
        self.assertFalse(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)

        # Add 1 handler twice, then remove
        logger.addHandler(handler_mock)
        logger.addHandler(handler_mock)
        self.assertTrue(logger.hasHandlers())
        logger.removeHandler(handler_mock)
        self.assertFalse(logger.hasHandlers())

    def tearDown(self):
        pass
