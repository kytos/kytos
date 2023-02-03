"""Module with identifier types for Links and Interfaces"""

import hashlib


class InterfaceID(str):
    """Interface Identifier"""

    __slots__ = ("switch", "port", "tuple")

    def __new__(cls, switch: str, port: int):
        return super().__new__(cls, f"{switch}:{port}")

    def __init__(self, switch: str, port: int):
        # Used for sorting, but can be accessed
        self.switch = switch
        self.port = port
        self.tuple = (switch, port)
        super().__init__()

    def __lt__(self, other):
        # Ensures that instances are sortable in a way that maintains backwards
        # compatibility when creating instances of LinkID
        if isinstance(other, InterfaceID):
            return self.tuple < other.tuple
        return NotImplemented

    def __getnewargs__(self):
        """To make sure it's pickleable"""
        return self.tuple


class LinkID(str):
    """Link Identifier"""

    def __new__(cls, interface_a: InterfaceID, interface_b: InterfaceID):
        raw_str = ":".join(sorted((interface_a, interface_b)))
        digest = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()
        return super().__new__(cls, digest)

    def __init__(self, interface_a: InterfaceID, interface_b: InterfaceID):
        self.interfaces = tuple(sorted((interface_a, interface_b)))
        super().__init__()

    def __getnewargs__(self):
        """To make sure it's pickleable"""
        return self.interfaces
