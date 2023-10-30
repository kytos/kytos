"""Test kytos.core.tag_ranges"""
from kytos.core.tag_ranges import (find_index_add, find_index_remove,
                                   range_addition, range_difference,
                                   range_intersection)


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
