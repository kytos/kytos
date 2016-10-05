"""Module with Kyco Events"""

from kyco.utils import now


#######################
# Base Events Classes #
#######################

class KycoEvent(object):
    """Base Event class.

    The event data will be passed on the content attribute, which should be a
    dictionary.

    Args:
        name (string): The name of the event. You should prepend with the name
                       of the napp.
        content (dict): Dictionary with all event informations.
    """

    def __init__(self, name=None, content=None):
        self.name = name
        self.content = content if content is not None else {}
        self.timestamp = now()

    @property
    def destination(self):
        return self.content.get('destination')

    def set_destination(self, destination):
        self.content['destination'] = destination

    @property
    def source(self):
        return self.content.get('source')

    def set_source(self, source):
        self.content['source'] = source
