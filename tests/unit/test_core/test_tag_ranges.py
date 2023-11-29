"""Test kytos.core.tag_ranges"""
import pytest

from kytos.core.exceptions import KytosInvalidTagRanges
from kytos.core.tag_ranges import (find_index_add, find_index_remove,
                                   get_special_tags, get_tag_ranges,
                                   get_validated_tags, map_singular_values,
                                   range_addition, range_difference,
                                   range_intersection)


def test_get_special_tags():
    """Test get_special_tags"""

    # "even_tags" is an hypotetical future special vlan
    default = ["untagged", "any", "even_tags"]

    tag_range = ["any", "any"]
    with pytest.raises(KytosInvalidTagRanges):
        get_special_tags(tag_range, default)

    tag_range = ["untagged", "any"]
    assert get_special_tags(tag_range, default) == tag_range

    tag_range = ["untagged", "error"]
    with pytest.raises(KytosInvalidTagRanges):
        get_special_tags(tag_range, default)


def test_map_singular_values():
    """Test map_singular_values"""
    mock_tag = 201
    result = map_singular_values(mock_tag)
    assert result == [201, 201]
    mock_tag = [201]
    result = map_singular_values(mock_tag)
    assert result == [201, 201]


def test_get_tag_ranges():
    """Test _get_tag_ranges"""
    mock_ranges = [100, [150], [200, 3000]]
    result = get_tag_ranges(mock_ranges)
    assert result == [[100, 100], [150, 150], [200, 3000]]

    # Empty
    mock_ranges = []
    with pytest.raises(KytosInvalidTagRanges):
        get_tag_ranges(mock_ranges)

    # Range not ordered
    mock_ranges = [[20, 19]]
    with pytest.raises(KytosInvalidTagRanges):
        get_tag_ranges(mock_ranges)

    # Ranges not ordered
    mock_ranges = [[20, 50], [30, 3000]]
    with pytest.raises(KytosInvalidTagRanges):
        get_tag_ranges(mock_ranges)

    # Unnecessary partition
    mock_ranges = [[20, 50], [51, 3000]]
    with pytest.raises(KytosInvalidTagRanges):
        get_tag_ranges(mock_ranges)

    # Repeated tag
    mock_ranges = [[20, 50], [50, 3000]]
    with pytest.raises(KytosInvalidTagRanges):
        get_tag_ranges(mock_ranges)

    # Over 4095
    mock_ranges = [[20, 50], [52, 4096]]
    with pytest.raises(KytosInvalidTagRanges):
        get_tag_ranges(mock_ranges)

    # Under 1
    mock_ranges = [[0, 50], [52, 3000]]
    with pytest.raises(KytosInvalidTagRanges):
        get_tag_ranges(mock_ranges)


def test_range_intersection():
    """Test range_intersection"""
    tags_a = [
        [3, 5], [7, 9], [11, 16], [21, 23], [25, 25], [27, 28], [30, 30]
    ]
    tags_b = [
        [1, 3], [6, 6], [10, 10], [12, 13], [15, 15], [17, 20], [22, 30]
    ]
    result = []
    iterator_result = range_intersection(tags_a, tags_b)
    for tag_range in iterator_result:
        result.append(tag_range)
    expected = [
        [3, 3], [12, 13], [15, 15], [22, 23], [25, 25], [27, 28], [30, 30]
    ]
    assert result == expected


def test_range_difference():
    """Test range_difference"""
    ranges_a = [[7, 10], [12, 12], [14, 14], [17, 19], [25, 27], [30, 30]]
    ranges_b = [[1, 1], [4, 5], [8, 9], [11, 14], [18, 26]]
    expected = [[7, 7], [10, 10], [17, 17], [27, 27], [30, 30]]
    actual = range_difference(ranges_a, ranges_b)
    assert expected == actual


def test_find_index_remove():
    """Test find_index_remove"""
    tag_ranges = [[20, 50], [200, 3000]]
    index = find_index_remove(tag_ranges, [20, 20])
    assert index == 0
    index = find_index_remove(tag_ranges, [10, 15])
    assert index is None
    index = find_index_remove(tag_ranges, [25, 30])
    assert index == 0


def test_find_index_add():
    """Test find_index_add"""
    tag_ranges = [[20, 20], [200, 3000]]
    index = find_index_add(tag_ranges, [10, 15])
    assert index == 0
    index = find_index_add(tag_ranges, [3004, 4000])
    assert index == 2
    index = find_index_add(tag_ranges, [50, 202])
    assert index is None


def test_range_addition():
    """Test range_addition"""
    ranges_a = [
        [3, 10], [20, 50], [60, 70], [80, 90], [100, 110],
        [112, 120], [130, 140], [150, 160]
    ]
    ranges_b = [
        [1, 1], [3, 3], [9, 22], [24, 55], [57, 62],
        [81, 101], [123, 128]
    ]
    expected_add = [
        [1, 1], [3, 55], [57, 70], [80, 110], [112, 120],
        [123, 128], [130, 140], [150, 160]
    ]
    expected_intersection = [
        [3, 3], [9, 10], [20, 22], [24, 50], [60, 62],
        [81, 90], [100, 101]
    ]
    result = range_addition(ranges_a, ranges_b)
    assert expected_add == result[0]
    assert expected_intersection == result[1]

    ranges_a = [[1, 4], [9, 15]]
    ranges_b = [[6, 7]]
    expected_add = [[1, 4], [6, 7], [9, 15]]
    expected_intersection = []
    result = range_addition(ranges_a, ranges_b)
    assert expected_add == result[0]
    assert expected_intersection == result[1]

    # Corner case, assuring not unnecessary divisions
    ranges_a = [[1, 2], [6, 7]]
    ranges_b = [[3, 4], [9, 10]]
    expected_add = [[1, 4], [6, 7], [9, 10]]
    expected_intersection = []
    result = range_addition(ranges_a, ranges_b)
    assert expected_add == result[0]
    assert expected_intersection == result[1]

    empty_range = []
    other_range = [[1, 100], [200, 400]]
    assert range_addition(empty_range, other_range) == (other_range, [])
    assert range_addition(other_range, empty_range) == (other_range, [])


async def test_get_validated_tags() -> None:
    """Test get_validated_tags"""
    result = get_validated_tags([1, 2])
    assert result == [1, 2]

    result = get_validated_tags([4])
    assert result == [4, 4]

    result = get_validated_tags([[1, 2], [4, 5]])
    assert result == [[1, 2], [4, 5]]

    with pytest.raises(KytosInvalidTagRanges):
        get_validated_tags("a")
    with pytest.raises(KytosInvalidTagRanges):
        get_validated_tags([1, 2, 3])
    with pytest.raises(KytosInvalidTagRanges):
        get_validated_tags([5, 2])
