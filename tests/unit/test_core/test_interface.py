"""Interface tests."""
# pylint: disable=attribute-defined-outside-init
import logging
import pickle
from unittest.mock import MagicMock, Mock

import pytest
from pyof.v0x04.common.port import PortFeatures

from kytos.core.common import EntityStatus
from kytos.core.exceptions import (KytosSetTagRangeError,
                                   KytosTagsAreNotAvailable,
                                   KytosTagsNotInTagRanges,
                                   KytosTagtypeNotSupported)
from kytos.core.interface import TAG, UNI, Interface
from kytos.core.switch import Switch

logging.basicConfig(level=logging.CRITICAL)


class TestTAG():
    """TAG tests."""

    def setup_method(self):
        """Create TAG object."""
        self.tag = TAG('vlan', 123)

    async def test_from_dict(self):
        """Test from_dict method."""
        tag_dict = {'tag_type': 'vlan_qinq', 'value': 456}
        tag = self.tag.from_dict(tag_dict)

        assert tag.tag_type == 'vlan_qinq'
        assert tag.value == 456

    async def test_as_dict(self):
        """Test as_dict method."""
        assert self.tag.as_dict() == {'tag_type': 'vlan', 'value': 123}

    async def test_from_json(self):
        """Test from_json method."""
        tag_json = '{"tag_type": "vlan_qinq", "value": 456}'
        tag = self.tag.from_json(tag_json)

        assert tag.tag_type == "vlan_qinq"
        assert tag.value == 456

    async def test_as_json(self):
        """Test as_json method."""
        assert self.tag.as_json() == '{"tag_type": "vlan", "value": 123}'

    async def test__repr__(self):
        """Test __repr__ method."""
        assert repr(self.tag) == "TAG('vlan', 123)"


# pylint: disable=protected-access, too-many-public-methods
class TestInterface():
    """Test Interfaces."""

    def setup_method(self):
        """Create interface object."""
        self.iface = self._get_v0x04_iface()

    async def test_repr(self):
        """Test repr() output."""
        expected = "Interface('name', 42, Switch('dpid'))"
        assert repr(self.iface) == expected

    @staticmethod
    def _get_v0x04_iface(*args, **kwargs):
        """Create a v0x04 interface object with optional extra arguments."""
        switch = Switch('dpid')
        switch.connection = Mock()
        switch.connection.protocol.version = 0x04
        switch.update_lastseen()
        return Interface('name', 42, switch, *args, **kwargs)

    async def test_speed_feature_none(self):
        """When port's current features is None."""
        self.iface.features = None
        assert self.iface.speed is None
        assert '' == self.iface.get_hr_speed()

    async def test_speed_feature_zero(self):
        """When port's current features is 0. E.g. port 65534."""
        self.iface.features = 0
        assert self.iface.speed is None
        assert '' == self.iface.get_hr_speed()

    async def test_1_tera_speed(self):
        """1Tb link."""
        self.iface.features = PortFeatures.OFPPF_1TB_FD
        assert 10**12 / 8 == self.iface.speed
        assert '1 Tbps' == self.iface.get_hr_speed()

    async def test_100_giga_speed(self):
        """100Gb link."""
        self.iface.features = PortFeatures.OFPPF_100GB_FD
        assert 100 * 10**9 / 8 == self.iface.speed
        assert '100 Gbps' == self.iface.get_hr_speed()

    async def test_40_giga_speed(self):
        """40Gb link."""
        self.iface.features = PortFeatures.OFPPF_40GB_FD
        assert 40 * 10**9 / 8 == self.iface.speed
        assert '40 Gbps' == self.iface.get_hr_speed()

    async def test_10_giga_speed(self):
        """10Gb link."""
        self.iface.features = PortFeatures.OFPPF_10GB_FD
        assert 10 * 10**9 / 8 == self.iface.speed
        assert '10 Gbps' == self.iface.get_hr_speed()

    async def test_1_giga_speed(self):
        """1Gb link."""
        self.iface.features = PortFeatures.OFPPF_1GB_FD
        assert 10**9 / 8 == self.iface.speed
        assert '1 Gbps' == self.iface.get_hr_speed()

    async def test_100_mega_speed(self):
        """100Mb link."""
        self.iface.features = PortFeatures.OFPPF_100MB_FD
        assert 100 * 10**6 / 8 == self.iface.speed
        assert '100 Mbps' == self.iface.get_hr_speed()

    async def test_10_mega_speed(self):
        """10Mb link."""
        self.iface.features = PortFeatures.OFPPF_10MB_FD
        assert 10 * 10**6 / 8 == self.iface.speed
        assert '10 Mbps' == self.iface.get_hr_speed()

    async def test_speed_setter(self):
        """Should return speed that was set and not features'."""
        expected_speed = 12345
        self.iface.set_custom_speed(expected_speed)
        actual_speed = self.iface.speed
        assert expected_speed == actual_speed

    async def test_speed_in_constructor(self):
        """Custom speed should override features'."""
        expected_speed = 6789
        iface = self._get_v0x04_iface(speed=expected_speed)
        assert expected_speed == iface.speed

    async def test_speed_removing_features(self):
        """Should return custom speed again when features becomes None."""
        custom_speed = 101112
        of_speed = 10 * 10**6 / 8
        iface = self._get_v0x04_iface(speed=custom_speed,
                                      features=PortFeatures.OFPPF_10MB_FD)
        assert of_speed == iface.speed
        iface.features = None
        assert custom_speed == iface.speed

    async def test_interface_available_tags_tag_ranges(self):
        """Test available_tags and tag_ranges on Interface class."""
        default_available = {'vlan': [[1, 4095]]}
        default_tag_ranges = {'vlan': [[1, 4095]]}
        default_special_vlans = {'vlan': ["untagged", "any"]}
        default_special_tags = {'vlan': ["untagged", "any"]}
        assert self.iface.available_tags == default_available
        assert self.iface.tag_ranges == default_tag_ranges
        assert self.iface.special_available_tags == default_special_vlans
        assert self.iface.special_tags == default_special_tags

        custom_available = {'vlan': [[10, 200], [210, 4095]]}
        custom_tag_ranges = {'vlan': [[1, 100], [200, 4095]]}
        custom_special_vlans = {'vlan': ["any"]}
        custom_special_tags = {'vlan': ["any"]}
        self.iface.set_available_tags_tag_ranges(
            custom_available, custom_tag_ranges,
            custom_special_vlans, custom_special_tags
        )
        assert self.iface.available_tags == custom_available
        assert self.iface.tag_ranges == custom_tag_ranges
        assert self.iface.special_available_tags == custom_special_vlans
        assert self.iface.special_tags == custom_special_tags

    async def test_interface_is_tag_available(self):
        """Test is_tag_available on Interface class."""
        max_range = 4096
        for tag in range(1, max_range):
            next_tag = self.iface.is_tag_available(tag)
            assert next_tag

        # test lower limit
        assert self.iface.is_tag_available(0) is False
        # test upper limit
        assert self.iface.is_tag_available(max_range) is False

    async def test_interface_use_tags(self, controller):
        """Test all use_tags on Interface class."""
        self.iface._notify_interface_tags = MagicMock()
        tags = [100, 200]
        # check use tag for the first time
        self.iface.use_tags(controller, tags)
        assert self.iface._notify_interface_tags.call_count == 1

        # check use tag for the second time
        with pytest.raises(KytosTagsAreNotAvailable):
            self.iface.use_tags(controller, tags)
        assert self.iface._notify_interface_tags.call_count == 1

        # check use tag after returning the tag to the pool as list
        self.iface.make_tags_available(controller, [tags])
        self.iface.use_tags(controller, [tags])
        assert self.iface._notify_interface_tags.call_count == 3

        with pytest.raises(KytosTagsAreNotAvailable):
            self.iface.use_tags(controller, [tags])
        assert self.iface._notify_interface_tags.call_count == 3

        with pytest.raises(KytosTagsAreNotAvailable):
            self.iface.use_tags(controller, [tags], use_lock=False)
        assert self.iface._notify_interface_tags.call_count == 3

        self.iface.use_tags(controller, "untagged")
        assert "untagged" not in self.iface.special_available_tags["vlan"]

    async def test_enable(self):
        """Test enable method."""
        self.iface.switch = MagicMock()

        self.iface.enable()

        self.iface.switch.enable.assert_called()
        assert self.iface._enabled

    async def test_get_endpoint(self):
        """Test get_endpoint method."""
        endpoint = ('endpoint', 'time')
        self.iface.endpoints = [endpoint]

        return_endpoint = self.iface.get_endpoint('endpoint')

        assert return_endpoint == endpoint

    async def test_add_endpoint(self):
        """Test add_endpoint method."""
        self.iface.add_endpoint('endpoint')

        assert len(self.iface.endpoints) == 1

    async def test_delete_endpoint(self):
        """Test delete_endpoint method."""
        endpoint = ('endpoint', 'time')
        self.iface.endpoints = [endpoint]

        self.iface.delete_endpoint('endpoint')

        assert len(self.iface.endpoints) == 0

    async def test_update_endpoint(self):
        """Test update_endpoint method."""
        endpoint = ('endpoint', 'time')
        self.iface.endpoints = [endpoint]

        self.iface.update_endpoint('endpoint')

        assert len(self.iface.endpoints) == 1

    async def test_update_link__none(self):
        """Test update_link method when this interface is not in link
           endpoints."""
        link = MagicMock()
        link.endpoint_a = MagicMock()
        link.endpoint_b = MagicMock()

        result = self.iface.update_link(link)

        assert result is False

    async def test_update_link__endpoint_a(self):
        """Test update_link method when this interface is the endpoint a."""
        interface = MagicMock()
        interface.link = None
        link = MagicMock()
        link.endpoint_a = self.iface
        link.endpoint_b = interface

        self.iface.update_link(link)

        assert self.iface.link == link
        assert interface.link == link

    async def test_update_link__endpoint_b(self):
        """Test update_link method when this interface is the endpoint b."""
        interface = MagicMock()
        interface.link = None
        link = MagicMock()
        link.endpoint_a = interface
        link.endpoint_b = self.iface

        self.iface.update_link(link)

        assert self.iface.link == link
        assert interface.link == link

    @staticmethod
    async def test_pickleable_id() -> None:
        """Test to make sure the id is pickleable."""
        switch = Switch("dpid1")
        interface = Interface("s1-eth1", 1, switch)
        pickled = pickle.dumps(interface.as_dict())
        intf_dict = pickle.loads(pickled)
        assert intf_dict["id"] == interface.id

    async def test_status_funcs(self) -> None:
        """Test status_funcs."""
        self.iface.enable()
        self.iface.activate()
        assert self.iface.is_active()
        Interface.register_status_func(
            "some_napp_some_func",
            lambda iface: EntityStatus.DOWN
        )
        Interface.register_status_reason_func(
            "some_napp_some_func",
            lambda iface: {'test_status'}
        )
        assert self.iface.status == EntityStatus.DOWN
        assert self.iface.status_reason == {'test_status'}
        Interface.register_status_func(
            "some_napp_some_func",
            lambda iface: None
        )
        Interface.register_status_reason_func(
            "some_napp_some_func",
            lambda iface: set()
        )
        assert self.iface.status == EntityStatus.UP
        assert self.iface.status_reason == set()

    async def test_default_tag_values(self) -> None:
        """Test default_tag_values property"""
        expected = {
            "vlan": [[1, 4095]],
            "vlan_qinq": [[1, 4095]],
            "mpls": [[1, 1048575]],
        }
        assert self.iface.default_tag_values == expected

    async def test_make_tags_available(self, controller) -> None:
        """Test make_tags_available"""
        available = {'vlan': [[300, 3000]]}
        tag_ranges = {'vlan': [[20, 20], [200, 3000]]}
        special_available_tags = {'vlan': []}
        special_tags = {'vlan': ["any"]}
        self.iface._notify_interface_tags = MagicMock()
        self.iface.set_available_tags_tag_ranges(
            available, tag_ranges,
            special_available_tags, special_tags
        )
        assert self.iface.available_tags == available
        assert self.iface.tag_ranges == tag_ranges

        with pytest.raises(KytosTagsNotInTagRanges):
            self.iface.make_tags_available(controller, [1, 20])
        assert self.iface._notify_interface_tags.call_count == 0

        with pytest.raises(KytosTagsNotInTagRanges):
            self.iface.make_tags_available(controller, [[1, 20]])
        assert self.iface._notify_interface_tags.call_count == 0

        assert not self.iface.make_tags_available(controller, [250, 280])
        assert self.iface._notify_interface_tags.call_count == 1

        with pytest.raises(KytosTagsNotInTagRanges):
            self.iface.make_tags_available(controller, [1, 1], use_lock=False)

        assert self.iface.make_tags_available(controller, 300) == [[300, 300]]

        with pytest.raises(KytosTagsNotInTagRanges):
            self.iface.make_tags_available(controller, "untagged")

        assert self.iface.make_tags_available(controller, "any") is None
        assert "any" in self.iface.special_available_tags["vlan"]
        assert self.iface.make_tags_available(controller, "any") == "any"

    async def test_set_tag_ranges(self, controller) -> None:
        """Test set_tag_ranges"""
        tag_ranges = [[20, 20], [200, 3000]]
        with pytest.raises(KytosTagtypeNotSupported):
            self.iface.set_tag_ranges(tag_ranges, 'vlan_qinq')

        self.iface.set_tag_ranges(tag_ranges, 'vlan')
        self.iface.use_tags(controller, [200, 250])
        ava_expected = [[20, 20], [251, 3000]]
        assert self.iface.tag_ranges['vlan'] == tag_ranges
        assert self.iface.available_tags['vlan'] == ava_expected

        tag_ranges = [[20, 20], [400, 1000]]
        with pytest.raises(KytosSetTagRangeError):
            self.iface.set_tag_ranges(tag_ranges, 'vlan')

    async def test_remove_tag_ranges(self) -> None:
        """Test remove_tag_ranges"""
        tag_ranges = [[20, 20], [200, 3000]]
        self.iface.set_tag_ranges(tag_ranges, 'vlan')
        assert self.iface.tag_ranges['vlan'] == tag_ranges

        with pytest.raises(KytosTagtypeNotSupported):
            self.iface.remove_tag_ranges('vlan_qinq')

        self.iface.remove_tag_ranges('vlan')
        default = [[1, 4095]]
        assert self.iface.tag_ranges['vlan'] == default

    def test_set_special_tags(self) -> None:
        """Test set_special_tags"""
        self.iface.special_available_tags["vlan"] = ["untagged"]
        tag_type = "error"
        special_tags = ["untagged", "any"]
        with pytest.raises(KytosTagtypeNotSupported):
            self.iface.set_special_tags(tag_type, special_tags)

        tag_type = "vlan"
        special_tags = ["untagged"]
        with pytest.raises(KytosSetTagRangeError):
            self.iface.set_special_tags(tag_type, special_tags)

        special_tags = ["any"]
        self.iface.set_special_tags(tag_type, special_tags)
        assert self.iface.special_available_tags["vlan"] == []
        assert self.iface.special_tags["vlan"] == ["any"]

    async def test_remove_tags(self) -> None:
        """Test _remove_tags"""
        available_tag = [[20, 20], [200, 3000]]
        tag_ranges = [[1, 4095]]
        self.iface.set_available_tags_tag_ranges(
            {'vlan': available_tag},
            {'vlan': tag_ranges},
            {'vlan': ["untagged", "any"]},
            {'vlan': ["untagged", "any"]}
        )
        ava_expected = [[20, 20], [241, 3000]]
        assert self.iface._remove_tags([200, 240])
        assert self.iface.available_tags['vlan'] == ava_expected
        ava_expected = [[241, 3000]]
        assert self.iface._remove_tags([20, 20])
        assert self.iface.available_tags['vlan'] == ava_expected
        ava_expected = [[241, 250], [400, 3000]]
        assert self.iface._remove_tags([251, 399])
        assert self.iface.available_tags['vlan'] == ava_expected
        assert self.iface._remove_tags([200, 240]) is False
        ava_expected = [[241, 250], [400, 499]]
        assert self.iface._remove_tags([500, 3000])
        assert self.iface.available_tags['vlan'] == ava_expected

    async def test_remove_tags_empty(self) -> None:
        """Test _remove_tags when available_tags is empty"""
        available_tag = []
        tag_ranges = [[1, 4095]]
        parameters = {
            "available_tag": {'vlan': available_tag},
            "tag_ranges": {'vlan': tag_ranges},
            "special_available_tags": {'vlan': ["untagged", "any"]},
            "special_tags": {'vlan': ["untagged", "any"]}
        }
        self.iface.set_available_tags_tag_ranges(**parameters)
        assert self.iface._remove_tags([4, 6]) is False
        assert self.iface.available_tags['vlan'] == []

    async def test_add_tags(self) -> None:
        """Test _add_tags"""
        available_tag = [[7, 10], [20, 30]]
        tag_ranges = [[1, 4095]]
        parameters = {
            "available_tag": {'vlan': available_tag},
            "tag_ranges": {'vlan': tag_ranges},
            "special_available_tags": {'vlan': ["untagged", "any"]},
            "special_tags": {'vlan': ["untagged", "any"]}
        }
        self.iface.set_available_tags_tag_ranges(**parameters)
        ava_expected = [[4, 10], [20, 30]]
        assert self.iface._add_tags([4, 6])
        assert self.iface.available_tags['vlan'] == ava_expected

        ava_expected = [[1, 2], [4, 10], [20, 30]]
        assert self.iface._add_tags([1, 2])
        assert self.iface.available_tags['vlan'] == ava_expected

        ava_expected = [[1, 2], [4, 10], [20, 35]]
        assert self.iface._add_tags([31, 35])
        assert self.iface.available_tags['vlan'] == ava_expected

        ava_expected = [[1, 2], [4, 10], [20, 35], [90, 90]]
        assert self.iface._add_tags([90, 90])
        assert self.iface.available_tags['vlan'] == ava_expected

        ava_expected = [[1, 2], [4, 10], [20, 90]]
        assert self.iface._add_tags([36, 89])
        assert self.iface.available_tags['vlan'] == ava_expected

        ava_expected = [[1, 2], [4, 12], [20, 90]]
        assert self.iface._add_tags([11, 12])
        assert self.iface.available_tags['vlan'] == ava_expected

        ava_expected = [[1, 2], [4, 12], [17, 90]]
        assert self.iface._add_tags([17, 19])
        assert self.iface.available_tags['vlan'] == ava_expected

        ava_expected = [[1, 2], [4, 12], [15, 15], [17, 90]]
        assert self.iface._add_tags([15, 15])
        assert self.iface.available_tags['vlan'] == ava_expected

        assert self.iface._add_tags([35, 98]) is False

    async def test_add_tags_empty(self) -> None:
        """Test _add_tags when available_tags is empty"""
        available_tag = []
        tag_ranges = [[1, 4095]]
        parameters = {
            "available_tag": {'vlan': available_tag},
            "tag_ranges": {'vlan': tag_ranges},
            "special_available_tags": {'vlan': ["untagged", "any"]},
            "special_tags": {'vlan': ["untagged", "any"]}
        }
        self.iface.set_available_tags_tag_ranges(**parameters)
        assert self.iface._add_tags([4, 6])
        assert self.iface.available_tags['vlan'] == [[4, 6]]

    async def test_notify_interface_tags(self, controller) -> None:
        """Test _notify_interface_tags"""
        name = "kytos/core.interface_tags"
        content = {"interface": self.iface}
        self.iface._notify_interface_tags(controller)
        event = controller.buffers.app.put.call_args[0][0]
        assert event.name == name
        assert event.content == content


class TestUNI():
    """UNI tests."""

    def setup_method(self):
        """Create UNI object."""
        switch = MagicMock()
        switch.id = '00:00:00:00:00:00:00:01'
        interface = Interface('name', 1, switch)
        user_tag = TAG('vlan', 123)
        self.uni = UNI(interface, user_tag)

    async def test__eq__(self):
        """Test __eq__ method."""
        user_tag = TAG('vlan', 456)
        interface = Interface('name', 2, MagicMock())
        other = UNI(interface, user_tag)

        assert (self.uni == other) is False

    async def test_is_valid(self):
        """Test is_valid method for a valid, invalid and none tag."""
        assert self.uni.is_valid()

        with pytest.raises(ValueError):
            TAG("some_type", 123)

        self.uni.user_tag = None
        assert self.uni.is_valid()

    async def test_is_reserved_valid_tag(self):
        """Test _is_reserved_valid_tag method for string TAG."""
        self.uni.user_tag = TAG("vlan", "untagged")
        assert self.uni.is_valid()

        self.uni.user_tag = TAG("vlan", "any")
        assert self.uni.is_valid()

        self.uni.user_tag = TAG("vlan", "2/4094")
        assert self.uni.is_valid() is False

    async def test_as_dict(self):
        """Test as_dict method."""
        expected_dict = {'interface_id': '00:00:00:00:00:00:00:01:1',
                         'tag': {'tag_type': 'vlan', 'value': 123}}
        assert self.uni.as_dict() == expected_dict

    async def test_as_json(self):
        """Test as_json method."""
        expected_json = '{"interface_id": "00:00:00:00:00:00:00:01:1", ' + \
                        '"tag": {"tag_type": "vlan", "value": 123}}'
        assert self.uni.as_json() == expected_json
