class SwitchID(str):
    pass

class InterfaceID(str):
    def __new__(cls, switch:SwitchID, port:int):
        return super().__new__(cls, f"{switch}:{port}")

class LinkID(str):
    def __new__(cls, interface_1:InterfaceID, interface_2:InterfaceID):
        return super().__new__(cls, ":".join(sorted((interface_1, interface_2))))
