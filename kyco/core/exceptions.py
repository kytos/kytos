"""Kyco Core-Defined Exceptions."""


class KycoCoreException(Exception):
    """Exception thrown when KycoCore is broken."""

    def __str__(self):
        """Return message of KycoCoreException."""
        return 'KycoCore exception: ' + super().__str__()


class KycoSwitchOfflineException(Exception):
    """Exception thrown when a switch is offline."""

    def __init__(self, switch):
        """Constructor receive the parameters below.

        Parameters:
            switch (:class:`~kyco.core.switch.Switch`): A switch offline.
        """
        super().__init__()
        self.switch = switch

    def __str__(self):
        """Return message of KycoSwitchOfflineException."""
        msg = 'The switch {} is not reachable. Please check the connection '
        msg += 'between the switch and the controller.'
        return msg.format(self.switch.dpid)


class KycoEventException(Exception):
    """Exception thrown when a KycoEvent have an illegal use."""

    def __init__(self, message="KycoEvent exception", event=None):
        """Constructor receive the parameters below.

        Parameters:
            message (string): message from KycoEventException.
            event (:class:`~kyco.core.events.KycoEvent`): Event malformed.
        """
        self.message = message
        self.event = event

    def __str__(self):
        """Return the full message from KycoEventException."""
        message = self.message
        if self.event:
            message += ". EventType: " + type(self.event)
        return message


class KycoWrongEventType(KycoEventException):
    """Exception related to EventType.

    When related to buffers, it means that the EventType is not allowed on
    that buffer.
    """

    pass

# Exceptions related  to NApps


class KycoNAppException(Exception):
    """Exception raised on a KycoNApp."""

    def __init__(self, message="KycoNApp exception"):
        """Constructor receive the paramters below.

        Parameters:
            message (string): message from KycoNAppException.
        """
        self.message = message

    def __str__(self):
        """Return the message from KycoNAppException."""
        return self.message


class KycoNAppMissingInitArgument(KycoNAppException):
    """Exception thrown when NApp have a missing init argument."""

    def __init__(self, message="KycoNAppMissingInitArgument"):
        """Constructor receive the parameters below.

        Args:
            message (str): Name of the missed argument.
        """
        super().__init__(message=message)
