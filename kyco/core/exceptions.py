"""Kyco Core-Defined Exceptions"""

# Buffers exceptions


class KycoEventException(Exception):
    """Event related exceptions"""
    def __init__(self, message="KycoEvent exception", event=None):
        self.message = message
        self.event = event

    def __str__(self):
        message = self.message
        if self.event:
            message += ". EventType: " + type(self.event)
        return message


class KycoWrongEventType(KycoEventException):
    """Exception related to EventType.

    When related to buffers, it means that the EventType is not allowed on
    that buffer."""
    pass

# Exceptions related  to NApps


class KycoNAppException(Exception):
    """Exception raised on a KycoNApp"""
    def __init__(self, message="KycoNApp exception"):
        self.message = message

    def __str__(self):
        return self.message


class KycoNAppMissingInitArgument(KycoNAppException):
    """Raised when a KycoNApp is instantiated without a required arg.

    Args:
        message (str): Name of the missed argument.
    """
    pass
