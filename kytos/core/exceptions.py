"""Kytos Core-Defined Exceptions."""


class KytosCoreException(Exception):
    """Exception thrown when KytosCore is broken."""

    def __str__(self):
        """Return message of KytosCoreException."""
        return 'KytosCore exception: ' + super().__str__()


class KytosSwitchOfflineException(Exception):
    """Exception thrown when a switch is offline."""

    def __init__(self, switch):
        """Constructor receive the parameters below.

        Parameters:
            switch (:class:`~kytos.core.switch.Switch`): A switch offline.
        """
        super().__init__()
        self.switch = switch

    def __str__(self):
        """Return message of KytosSwitchOfflineException."""
        msg = 'The switch {} is not reachable. Please check the connection '
        msg += 'between the switch and the controller.'
        return msg.format(self.switch.dpid)


class KytosEventException(Exception):
    """Exception thrown when a KytosEvent have an illegal use."""

    def __init__(self, message="KytosEvent exception", event=None):
        """Constructor receive the parameters below.

        Parameters:
            message (string): message from KytosEventException.
            event (:class:`~kytos.core.events.KytosEvent`): Event malformed.
        """
        super().__init__()
        self.message = message
        self.event = event

    def __str__(self):
        """Return the full message from KytosEventException."""
        message = self.message
        if self.event:
            message += ". EventType: " + type(self.event)
        return message


class KytosWrongEventType(KytosEventException):
    """Exception related to EventType.

    When related to buffers, it means that the EventType is not allowed on
    that buffer.
    """

    pass

# Exceptions related  to NApps


class KytosNAppException(Exception):
    """Exception raised on a KytosNApp."""

    def __init__(self, message="KytosNApp exception"):
        """Constructor receive the paramters below.

        Parameters:
            message (string): message from KytosNAppException.
        """
        super().__init__()
        self.message = message

    def __str__(self):
        """Return the message from KytosNAppException."""
        return self.message


class KytosNAppMissingInitArgument(KytosNAppException):
    """Exception thrown when NApp have a missing init argument."""

    def __init__(self, message="KytosNAppMissingInitArgument"):
        """Constructor receive the parameters below.

        Args:
            message (str): Name of the missed argument.
        """
        super().__init__(message=message)
