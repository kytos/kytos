"""Module with main classes related to Flows"""

import hashlib
import json

from pyof.v0x01.common.action import ActionOutput, ActionType
from pyof.v0x01.common.flow_match import Match
from pyof.v0x01.controller2switch.flow_mod import FlowMod


class Flow(object):
    """
    This class represents a Flow installed or to be installed inside the
    switch. A flow, in this case is represented by a Match object and a set of
    actions that should occur in case any match happen.
    """
    def __init__(self, idle_timeout=0, hard_timeout=0, priority=0,
                 table_id=0xff, buffer_id=0xff, in_port=None, dl_src=None,
                 dl_dst=None, dl_vlan=None, dl_type=None, nw_proto=None,
                 nw_src=None, nw_dst=None, tp_src=None, tp_dst=None,
                 actions=None):
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
        """Returns the hash of the object"""
        return hash(self)

    def __hash__(self):
        """
        Calculates the hash of the object by using the hashlib we use md5 of
        strings.
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
            hash_result.update(str(hash(action)).encode('utf-8'))

        return hash_result.hexdigest()

    def as_json(self):
        """Returns the representation of a flow in a json format"""
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
                                   "tp_dst": self.tp_dst,
                                   "actions": self.actions}}

        actions = []
        for action in self.actions:
            actions.append(action.as_dict())

        dictionary_rep[self.id][actions] = actions

        return json.dumps(dictionary_rep)

    @staticmethod
    def from_json(json_content):
        """Builds a Flow object from a json"""
        dict_content = json.loads(json_content)
        return Flow.from_dict(dict_content)

    @staticmethod
    def from_dict(dict_content):
        """Builds a Flow object from a json"""
        flow_fields = dict_content['flow']
        flow = Flow()
        flow.idle_timeout = flow_fields['idle_timeout']
        flow.hard_timeout = flow_fields['hard_timeout']
        flow.priority = flow_fields['buffer_id']
        flow.priority = flow_fields['table_id']
        flow.priority = flow_fields['priority']
        flow.in_port = flow_fields['in_port']
        flow.dl_src = flow_fields['dl_src']
        flow.dl_dst = flow_fields['dl_dst']
        flow.dl_vlan = flow_fields['dl_vlan']
        flow.dl_type = flow_fields['dl_type']
        flow.nw_src = flow_fields['nw_src']
        flow.nw_dst = flow_fields['nw_dst']
        flow.tp_src = flow_fields['tp_src']
        flow.tp_dst = flow_fields['tp_dst']

        actions = []
        for dict_action in dict_content['actions']:
            action = OutputAction.from_dict(dict_action)  # Only Output
            actions.append(action)

        flow.actions = actions

    @staticmethod
    def from_flow_stats(flow_stats):
        """Builds a new Flow Object from a stats_reply """
        flow = Flow()
        flow.idle_timeout = flow_stats.idle_timeout
        flow.hard_timeout = flow_stats.hard_timeout
        flow.priority = flow_stats.priority
        flow.table_id = flow_stats.table_id
        flow.in_port = flow_stats.match.in_port
        flow.dl_src = flow_stats.match.dl_src
        flow.dl_dst = flow_stats.match.dl_dst
        flow.dl_vlan = flow_stats.match.dl_vlan
        flow.dl_type = flow_stats.match.dl_type
        flow.nw_src = flow_stats.match.nw_src
        flow.nw_dst = flow_stats.match.nw_dst
        flow.tp_src = flow_stats.match.tp_src
        flow.tp_dst = flow_stats.match.tp_dst
        flow.actions = []
        for ofp_action in flow_stats.actions:
            if ofp_action.action_type == ActionType.OFPAT_OUTPUT:
                flow.actions.append(OutputAction.from_of_action(ofp_action))
        return flow

    def as_flow_mod(self, flow_type):
        """Transform a Flow object into a flow_mod message"""
        flow_mod = FlowMod()
        flow_mod.command = flow_type
        flow_mod.buffer_id = self.buffer_id
        flow_mod.idle_timeout = self.idle_timeout
        flow_mod.hard_timeout = self.hard_timeout
        flow_mod.priority = self.priority
        flow_mod.match = Match()
        flow_mod.match.in_port = self.in_port
        flow_mod.match.dl_src = self.dl_src
        flow_mod.match.dl_dst = self.dl_dst
        flow_mod.match.dl_vlan = self.dl_vlan
        flow_mod.match.dl_type = self.dl_type
        flow_mod.match.nw_src = self.nw_src
        flow_mod.match.nw_dst = self.nw_dst
        flow_mod.match.tp_src = self.tp_src
        flow_mod.match.tp_dst = self.tp_dst
        flow_mod.match.fill_wildcards()
        for action in self.actions:
            flow_mod.actions.append(action.as_of_action())
        return flow_mod


class FlowAction(object):
    """The instances of this class represent action to be executed once a flow
    is activated"""

    @staticmethod
    def from_dict(dict_content):
        """Builds one of the FlowActions from a dictionary"""
        pass


class OutputAction(FlowAction):
    """This class represents the action of forwarding network packets into a
    given port"""
    def __init__(self, output_port):
        self.output_port = output_port

    def as_of_action(self):
        """Builds a Action Output from this action"""
        return ActionOutput(port=self.output_port)

    def as_dict(self):
        """Returns this action as a dict"""
        return {"type": "action_output",
                "port": self.output_port}

    @staticmethod
    def from_dict(dict_content):
        """Builds an Output Action from a dictionary"""
        return OutputAction(output_port=dict_content['port'])

    def __hash__(self):
        """Returns the (unambiguous) representation of the Object"""
        hash_result = hashlib.md5()
        hash_result.update("OutputAction(output_port={})".encode('utf-8'))
        return hash_result.hexdigest()

    @staticmethod
    def from_of_action(ofp_action):
        """Builds a OutputAction from python-openflow ActionOutpud"""
        return OutputAction(output_port=ofp_action.port)


class DLChangeAction(FlowAction):
    """This action represents the change in the packet hw source/destination
    address"""
    def __init__(self, dl_src=None, dl_dst=None):
        self.dl_src = dl_src
        self.dl_dst = dl_dst


class NWChangeAction(FlowAction):
    """This action represents the change in the packet ip source/destination
    address"""
    def __init__(self, nw_src, nw_dst):
        self.nw_src = nw_src
        self.nw_dst = nw_dst
