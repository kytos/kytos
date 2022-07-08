class SwitchID(str):
    pass

class InterfaceID(str):
    __slots__ = ("switch", "port")
    def __new__(cls, switch:SwitchID, port:int):
        return super().__new__(cls, f"{switch}:{port}")
    def __init__(self, switch:SwitchID, port:int):
        #Used for sorting, but can be accessed
        self.switch = switch
        self.port = port

    def __lt__(self, other):
        # Ensures that instances are sortable in a way that maintains backwards
        # compatibility when creating instances of LinkID
        dpid_a = self.switch
        port_a = self.port
        dpid_b = other.switch
        port_b = other.port
        if dpid_a < dpid_b:
            return True
        elif dpid_a == dpid_b and port_a < port_b:
            return True
        else:
            return False

class LinkID(str):
    def __new__(cls, interface_1:InterfaceID, interface_2:InterfaceID):
        return super().__new__(cls, ":".join(sorted((interface_1, interface_2))))
