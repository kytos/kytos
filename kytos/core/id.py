"""Module with identifier types for Links and Interfaces"""

import hashlib


class InterfaceID(str):
    """Interface Identifier"""

    __slots__ = ("switch", "port")

    def __new__(cls, switch: str, port: int):
        return super().__new__(cls, f"{switch}:{port}")

    def __init__(self, switch: str, port: int):
        # Used for sorting, but can be accessed
        self.switch = switch
        self.port = port
        super().__init__()

    def __lt__(self, other):
        # Ensures that instances are sortable in a way that maintains backwards
        # compatibility when creating instances of LinkID
        dpid_a = self.switch
        port_a = self.port
        dpid_b = other.switch
        port_b = other.port
        if dpid_a < dpid_b:
            return True
        return dpid_a == dpid_b and port_a < port_b


class LinkID(str):
    """Link Identifier"""

    def __new__(cls, interface_1: InterfaceID, interface_2: InterfaceID):
        raw_str = ":".join(sorted((interface_1, interface_2)))
        digest = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()
        return super().__new__(cls, digest)
