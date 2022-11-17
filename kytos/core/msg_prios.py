"""Queue message priorities."""

from pyof.v0x04.common.header import Type


def of_msg_prio(msg_type: int) -> int:
    """Get OpenFlow message priority.

    The lower the number the higher the priority, if same priority, then it
    would be ordered ascending by KytosEvent timestamp."""
    prios = {
        Type.OFPT_FLOW_MOD.value: 1000,
        Type.OFPT_BARRIER_REQUEST.value: 1000
    }
    return prios.get(msg_type, 0)
