"""Module with Kyco Events"""


class KycoEvent(object):
    def __init__(self, context):
        self.context = context


class KycoCoreEvent(KycoEvent):
    pass


class KycoRawEvent(KycoCoreEvent):
    pass


class KycoRawConnectionUp(KycoRawEvent):
    pass


class KycoSwitchUp(KycoCoreEvent):
    pass


class KycoRawConnectionDown(KycoRawEvent):
    pass


class KycoSwitchDown(KycoCoreEvent):
    pass


class KycoRawOpenFlowMessageIn(KycoRawEvent):
    pass


class KycoMsgEvent(KycoCoreEvent):
    pass


class KycoAppEvent(KycoEvent):
    pass


class KycoAppInstalled(KycoCoreEvent):
    pass


class KycoAppLoaded(KycoCoreEvent):
    pass


class KycoAppUninstalled(KycoCoreEvent):
    pass


class KycoAppUnloaded(KycoCoreEvent):
    pass


class KycoServerDown(KycoCoreEvent):
    pass
