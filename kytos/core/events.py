"""Module with Kytos Events."""

from kytos.core.helpers import now


class KytosEvent(object):
    """Base Event class.

    The event data will be passed on the content attribute, which should be a
    dictionary.
    """

    def __init__(self, name=None, content=None):
        """Constructor of KytosEvent receive the parameters below.

        Args:
            name (string): The name of the event. You should prepend with
                           the name of the napp.
            content (dict): Dictionary with all event informations.
        """
        self.name = name
        self.content = content if content is not None else {}
        self.timestamp = now()

    @property
    def destination(self):
        """Return the destination of KytosEvent."""
        return self.content.get('destination')

    def set_destination(self, destination):
        """Update the destination of KytosEvent.

        Parameters:
            destination (string): destination of  KytosEvent.
        """
        self.content['destination'] = destination

    @property
    def source(self):
        """Return the source of KytosEvent."""
        return self.content.get('source')

    def set_source(self, source):
        """Update the source of KytosEvent.

        Parameters:
            source (string): source of KytosEvent.
        """
        self.content['source'] = source

    @property
    def message(self):
        """Return the message carried by the event if it exists.

        If there is any OpenFlow message on the event, then it will be stored
        on the 'message' key of the 'content' attribute. So, if there is any
        message we return it, if not, we return None.

        Returns:
            A python OpenfFlow message instance if it exists.
            None otherwise.
        """
        try:
            return self.content['message']
        except KeyError:
            return None
