"""Methods for list of ranges [inclusive, inclusive]"""
import bisect
from typing import Iterator, Optional, Union

from kytos.core.exceptions import KytosInvalidRanges


def map_singular_values(tag_range: Union[int, list[int]]):
    """Change integer or singular interger list to
    list[int, int] when necessary"""
    if isinstance(tag_range, int):
        tag_range = [tag_range] * 2
    elif len(tag_range) == 1:
        tag_range = [tag_range[0]] * 2
    return tag_range


def get_tag_ranges(ranges: list[list[int]]):
    """Get tag_ranges and check validity:
    - It should be ordered
    - Not unnecessary partition (eg. [[10,20],[20,30]])
    - Singular intergers are changed to ranges (eg. [10] to [[10, 10]])
    The ranges are understood as [inclusive, inclusive]"""
    if len(ranges) < 1:
        msg = "tag_ranges is empty"
        raise KytosInvalidRanges(msg)
    last_tag = 0
    ranges_n = len(ranges)
    for i in range(0, ranges_n):
        ranges[i] = map_singular_values(ranges[i])
        if ranges[i][0] > ranges[i][1]:
            msg = f"The range {ranges[i]} is not ordered"
            raise KytosInvalidRanges(msg)
        if last_tag and last_tag > ranges[i][0]:
            msg = f"tag_ranges is not ordered. {last_tag}"\
                     f" is higher than {ranges[i][0]}"
            raise KytosInvalidRanges(msg)
        if last_tag and last_tag == ranges[i][0] - 1:
            msg = f"tag_ranges has an unnecessary partition. "\
                     f"{last_tag} is before to {ranges[i][0]}"
            raise KytosInvalidRanges(msg)
        if last_tag and last_tag == ranges[i][0]:
            msg = f"tag_ranges has repetition. {ranges[i-1]}"\
                     f" have same values as {ranges[i]}"
            raise KytosInvalidRanges(msg)
        last_tag = ranges[i][1]
    if ranges[-1][1] > 4095:
        msg = "Maximum value for tag_ranges is 4095"
        raise KytosInvalidRanges(msg)
    if ranges[0][0] < 1:
        msg = "Minimum value for tag_ranges is 1"
        raise KytosInvalidRanges(msg)
    return ranges


def range_intersection(
    ranges_a: list[list[int]],
    ranges_b: list[list[int]]
) -> Iterator[list[int]]:
    """Returns an iterator of an intersection between
    two list of ranges"""
    a_i, b_i = 0, 0
    while a_i < len(ranges_a) and b_i < len(ranges_b):
        fst_a, snd_a = ranges_a[a_i]
        fst_b, snd_b = ranges_b[b_i]
        # Moving forward with non-intersection
        if snd_a < fst_b:
            a_i += 1
        elif snd_b < fst_a:
            b_i += 1
        else:
            # Intersection
            intersection_start = max(fst_a, fst_b)
            intersection_end = min(snd_a, snd_b)
            yield [intersection_start, intersection_end]
            if snd_a < snd_b:
                a_i += 1
            else:
                b_i += 1


def range_difference(
    ranges_a: list[list[int]],
    ranges_b: list[list[int]]
) -> list[list[int]]:
    """The operation is (ranges_a - ranges_b).
    This method simulates difference of sets. E.g.:
    [[10, 15]] - [[4, 11], [14, 45]] = [[12, 13]]
    """
    #print(f"RANGES -> {ranges_a} - {ranges_b}")
    if not ranges_a:
        return []
    if not ranges_b:
        return ranges_a
    result = []
    a_i, b_i = 0, 0
    update = True
    while a_i < len(ranges_a) and b_i < len(ranges_b):
        if update:
            start_a, end_a = ranges_a[a_i]
        else:
            update = True
        start_b, end_b = ranges_b[b_i]
        # Moving forward with non-intersection
        if end_a < start_b:
            result.append([start_a, end_a])
            a_i += 1
        elif end_b < start_a:
            b_i += 1
        else:
            # Intersection
            if start_a < start_b:
                result.append([start_a, start_b - 1])
            if end_a > end_b:
                start_a = end_b + 1
                update = False
                b_i += 1
            else:
                a_i += 1
    # Append last intersection and the rest of ranges_a
    while a_i < len(ranges_a):
        if update:
            start_a, end_a = ranges_a[a_i]
        else:
            update = True
        result.append([start_a, end_a])
        a_i += 1
    return result


def range_addition(
    ranges_a: list[list[int]],
    ranges_b: list[list[int]]
) -> tuple[list[list[int]], list[list[int]]]:
    """Addition between two ranges.
     Simulates the addition between two sets.
     Return[adittion product, intersection]"""
    if not ranges_b:
        return ranges_a
    if not ranges_a:
        return ranges_b
    result = []
    conflict = []
    a_i = b_i = 0
    len_a = len(ranges_a)
    len_b = len(ranges_b)
    while a_i < len_a or b_i < len_b:
        if (a_i < len_a and
                (b_i >= len_b or ranges_a[a_i][1] < ranges_b[b_i][0] - 1)):
            result.append(ranges_a[a_i])
            a_i += 1
        elif (b_i < len_b and
                (a_i >= len_a or ranges_b[b_i][1] < ranges_a[a_i][0] - 1)):
            result.append(ranges_b[b_i])
            b_i += 1
        # Intersection and continuos ranges
        else:
            fst = max(ranges_a[a_i][0], ranges_b[b_i][0])
            snd = min(ranges_a[a_i][1], ranges_b[b_i][1])
            if fst <= snd:
                conflict.append([fst, snd])
            new_range = [
                min(ranges_a[a_i][0], ranges_b[b_i][0]),
                max(ranges_a[a_i][1], ranges_b[b_i][1])
            ]
            a_i += 1
            b_i += 1
            while a_i < len_a or b_i < len_b:
                if a_i < len_a and (ranges_a[a_i][0] <= new_range[1] + 1):
                    if ranges_a[a_i][0] <= new_range[1]:
                        conflict.append([
                            max(ranges_a[a_i][0], new_range[0]),
                            min(ranges_a[a_i][1], new_range[1])
                        ])
                    new_range[1] = max(ranges_a[a_i][1], new_range[1])
                    a_i += 1
                elif b_i < len_b and (ranges_b[b_i][0] <= new_range[1] + 1):
                    if ranges_b[b_i][0] <= new_range[1]:
                        conflict.append([
                            max(ranges_b[b_i][0], new_range[0]),
                            min(ranges_b[b_i][1], new_range[1])
                        ])
                    new_range[1] = max(ranges_b[b_i][1], new_range[1])
                    b_i += 1
                else:
                    break
            result.append(new_range)
    return result, conflict


def find_index_remove(
    available_tags: list[list[int]],
    tag_range: list[int]
) -> Optional[int]:
    """Find the index of tags in available_tags to be removed"""
    index = bisect.bisect_left(available_tags, tag_range)
    if (index < len(available_tags) and
            tag_range[0] >= available_tags[index][0] and
            tag_range[1] <= available_tags[index][1]):
        return index
    if (index - 1 > -1 and
            tag_range[0] >= available_tags[index-1][0] and
            tag_range[1] <= available_tags[index-1][1]):
        return index - 1
    return None


def find_index_add(
    available_tags: list[list[int]],
    tags: list[int]
) -> Optional[int]:
    """Find the index of tags in available_tags to be added.
    This method assumes that tags is within self.tag_ranges"""
    index = bisect.bisect_left(available_tags, tags)
    if (index == 0 or tags[0] > available_tags[index-1][1]) and \
       (index == len(available_tags) or
            tags[1] < available_tags[index][0]):
        return index
    return None
