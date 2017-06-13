"""Module with main classes related to Flows."""

import hashlib
import json

from pyof.v0x01.common.action import ActionOutput, ActionType
from pyof.v0x01.common.flow_match import Match
from pyof.v0x01.controller2switch.flow_mod import FlowMod, FlowModCommand


class Flow(object):
    """Class to abstract a Flow to switches.

    This class represents a Flow installed or to be installed inside the
    switch. A flow, in this case is represented by a Match object and a set of
    actions that should occur in case any match happen.
    """

    def __init__(self, idle_timeout=0, hard_timeout=0, priority=0,  # noqa
                 table_id=0xff, buffer_id=None, in_port=None, dl_src=None,
                 dl_dst=None, dl_vlan=None, dl_type=None, nw_proto=None,
                 nw_src=None, nw_dst=None, tp_src=None, tp_dst=None,
                 actions=None):
        """Constructor receive the parameters below.

        Parameters:
           idle_timeout (int): Idle time before discarding in seconds.
           hard_timeout (int): Max time before discarding in seconds.
           priority (int): Priority level of flow entry.
           table_id (int): The index of a single table or 0xff for all tables.
           buffer_id (int): Buffered packet to apply.
           dl_src (HWAddress): Ethernet source address.
           dl_dst (HWAddress): Ethernet destination address.
           dl_vlan (int): Input VLAN id.
           dl_type (int): Ethernet frame type.
           nw_proto (int): IP protocol or lower 8 bits of ARP opcode.
           nw_src (IPAddress): IP source address.
           nw_dst (IPAddress): IP destination address.
           tp_src (int): TCP/UDP source port.
           tp_dst (int): TCP/UDP destination port.
           actions (ListOfAction): List of action to apply.
        """
        if actions is None:
            actions = []
        self.idle_timeout = idle_timeout
        self.hard_timeout = hard_timeout
        self.priority = priority
        self.table_id = table_id
        self.buffer_id = buffer_id
        self.in_port = in_port
        self.dl_src = dl_src
        self.dl_dst = dl_dst
        self.dl_vlan = dl_vlan
        self.dl_type = dl_type
        self.nw_proto = nw_proto
        self.nw_src = nw_src
        self.nw_dst = nw_dst
        self.tp_src = tp_src
        self.tp_dst = tp_dst
        self.actions = actions

    @property
    def id(self):
        """Return the hash of the object.

        Calculates the hash of the object by using the hashlib we use md5 of
        strings.

        Returns:
            hash (string): Hash of object.
        """
        hash_result = hashlib.md5()
        hash_result.update(str(self.idle_timeout).encode('utf-8'))
        hash_result.update(str(self.hard_timeout).encode('utf-8'))
        hash_result.update(str(self.priority).encode('utf-8'))
        hash_result.update(str(self.table_id).encode('utf-8'))
        hash_result.update(str(self.buffer_id).encode('utf-8'))
        hash_result.update(str(self.in_port).encode('utf-8'))
        hash_result.update(str(self.dl_src).encode('utf-8'))
        hash_result.update(str(self.dl_dst).encode('utf-8'))
        hash_result.update(str(self.dl_vlan).encode('utf-8'))
        hash_result.update(str(self.dl_type).encode('utf-8'))
        hash_result.update(str(self.nw_proto).encode('utf-8'))
        hash_result.update(str(self.nw_src).encode('utf-8'))
        hash_result.update(str(self.nw_dst).encode('utf-8'))
        hash_result.update(str(self.tp_src).encode('utf-8'))
        hash_result.update(str(self.tp_dst).encode('utf-8'))
        for action in self.actions:
            hash_result.update(action.id.encode('utf-8'))

        return hash_result.hexdigest()

    def as_dict(self):
        """Return the representation of a flow as a python dictionary.

        Returns:
            dictionary (dict): Dictionary using flow attributes.
        """
        dictionary_rep = {"flow": {"self.id": self.id,
                                   "idle_timeout": self.idle_timeout,
                                   "hard_timeout": self.hard_timeout,
                                   "priority": self.priority,
                                   "table_id": self.table_id,
                                   "buffer_id": self.buffer_id,
                                   "in_port": self.in_port,
                                   "dl_src": self.dl_src,
                                   "dl_dst": self.dl_dst,
                                   "dl_vlan": self.dl_vlan,
                                   "dl_type": self.dl_type,
                                   "nw_src": self.nw_src,
                                   "nw_dst": self.nw_dst,
                                   "tp_src": self.tp_src,
                                   "tp_dst": self.tp_dst}}

        actions = []
        for action in self.actions:
            actions.append(action.as_dict())

        dictionary_rep["flow"]["actions"] = actions

        return dictionary_rep

    def as_json(self):
        """Return the representation of a flow in a json format.

        Returns:
            json (string): Json string using flow attributes.
        """
        return json.dumps(self.as_dict())

    @staticmethod
    def from_json(json_content):
        """Build a Flow object from a json.

        Parameters:
            json_content (string): Json string with flow attributes.

        Returns:
            flow (:class:`~kytos.core.flow.Flow`): Flow built from json.
        """
        dict_content = json.loads(json_content)
        return Flow.from_dict(dict_content)

    @staticmethod
    def from_dict(dict_content):
        """Build a Flow object from a python dict.

        Parameters:
            dict_content (dict): Python dictionary with flow attributes.

        Returns:
            flow (:class:`~kytos.core.flow.Flow`): Flow built from json.
        """
        flow = Flow()

        for attribute_name, value in dict_content.items():
            # "actions" key has a list of actions as value, and each action on
            # the list must be created separately
            if attribute_name == "actions":
                for action_dict in value:
                    action = OutputAction.from_dict(action_dict)
                    flow.actions.append(action)
            else:
                setattr(flow, attribute_name, value)

        return flow

    @staticmethod
    def from_flow_stats(flow_stats):
        """Build a new Flow Object from a stats_reply.

        Parameters:
         stats_reply (StatsReply): Stats Reply Object.

        Returns:
         flow (:class:`~kytos.core.flow.Flow`): Flow built from json.
        """
        flow = Flow()
        flow.idle_timeout = flow_stats.idle_timeout.value
        flow.hard_timeout = flow_stats.hard_timeout.value
        flow.priority = flow_stats.priority.value
        flow.table_id = flow_stats.table_id.value
        flow.in_port = flow_stats.match.in_port.value
        flow.dl_src = flow_stats.match.dl_src.value
        flow.dl_dst = flow_stats.match.dl_dst.value
        flow.dl_vlan = flow_stats.match.dl_vlan.value
        flow.dl_type = flow_stats.match.dl_type.value
        flow.nw_src = flow_stats.match.nw_src.value
        flow.nw_dst = flow_stats.match.nw_dst.value
        flow.tp_src = flow_stats.match.tp_src.value
        flow.tp_dst = flow_stats.match.tp_dst.value
        flow.actions = []
        for ofp_action in flow_stats.actions:
            if ofp_action.action_type == ActionType.OFPAT_OUTPUT:
                flow.actions.append(OutputAction.from_of_action(ofp_action))
        return flow

    def as_flow_mod(self, flow_type=FlowModCommand.OFPFC_ADD):
        """Transform a Flow object into a flow_mod message.

        Parameters:
            flow_type (FlowModCommand): type of flow_mod to be converted.

        Returns:
            flow_mod (FlowMod): Instance of FlowMod with Flow attributes.
        """
        flow_mod = FlowMod()
        flow_mod.command = flow_type
        flow_mod_attributes = ['buffer_id', 'idle_timeout', 'hard_timeout',
                               'priority']

        for attribute_name in flow_mod_attributes:
            value = getattr(self, attribute_name)
            if value is not None:
                setattr(flow_mod, attribute_name, value)

        flow_mod.match = Match()
        match_attributes = ['in_port', 'dl_src', 'dl_dst', 'dl_vlan',
                            'dl_type', 'nw_src', 'nw_dst', 'tp_dst']

        for attribute_name in match_attributes:
            value = getattr(self, attribute_name)
            if value is not None:
                setattr(flow_mod.match, attribute_name, value)

        if self.actions is not None:
            for action in self.actions:
                flow_mod.actions.append(action.as_of_action())
        return flow_mod


class FlowAction(object):
    """FlowAction represents a action to be executed once a flow is actived."""

    @staticmethod
    def from_dict(dict_content):
        """Build one of the FlowActions from a dictionary.

        Parameters:
            dict_content (dict): Python dictionary to build a FlowAction.
        """
        pass


class OutputAction(FlowAction):
    """FlowAction represents a change in forwarding network into a port."""

    def __init__(self, output_port):
        """Constructor receive the parameters below.

        Parameters:
            output_port (int): Specific port number.
        """
        self.output_port = output_port

    def as_of_action(self):
        """Build a Action Output from this action.

        Returns:
            output_action (:class:`~kytos.core.flow.OutputAction`):
                A instance of OutputAction.
        """
        return ActionOutput(port=self.output_port)

    def as_dict(self):
        """Return this action as a python dictionary.

        Returns:
            dictionary (dict): Dict that represent a OutputAction.
        """
        return {"type": "action_output",
                "port": self.output_port}

    @staticmethod
    def from_dict(dict_content):
        """Build an OutputAction from a dictionary.

        Parameters:
          dict_content (dict): Python dictionary with OutputAction attribute.

        Returns:
          output_action (:class:`~kytos.core.flow.OutputAction`):
                A instance of OutputAction.
        """
        return OutputAction(output_port=dict_content['port'])

    @property
    def id(self):
        """Return the (unambiguous) representation of the object.

        Returns:
            string: string to represent the instance object.
        """
        hash_result = hashlib.md5()
        hash_result.update(str(self.as_dict()).encode('utf-8'))
        return hash_result.hexdigest()

    @staticmethod
    def from_of_action(ofp_action):
        """Build a OutputAction from python-openflow ActionOutput.

        Parameter:
            ofp_action (ActionOutput): Action used to create OutputAction.

        Returns:
            output_action (:class:`~kytos.core.flow.OutputAction`):
                A instance of OutputAction.
        """
        return OutputAction(output_port=ofp_action.port.value)


class DLChangeAction(FlowAction):
    """FlowAction that represents a change in hardware address."""

    def __init__(self, dl_src=None, dl_dst=None):
        """Constructor receive the parameters below.

        Parameters:
           dl_src (HWAddress): Ethernet source address.
           dl_dst (HWAddress): Ethernet destination address.
        """
        self.dl_src = dl_src
        self.dl_dst = dl_dst


class NWChangeAction(FlowAction):
    """FlowAction that represents new change in ip address."""

    def __init__(self, nw_src, nw_dst):
        """Contructor receive the parameters below.

        Parameters:
           nw_src (IPAddress): IP source address.
           nw_dst (IPAddress): IP destination address.
        """
        self.nw_src = nw_src
        self.nw_dst = nw_dst
