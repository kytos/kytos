"""Kyco Core-Defined Exceptions"""

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
