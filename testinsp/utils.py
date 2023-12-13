from subprocess import check_output
from json import load, loads
import re
import numbers


class GenericCompareEx(Exception):
    pass

class NotComparable(GenericCompareEx):
    pass

class ItemDifference(GenericCompareEx):
    pass

class DifferentSize(GenericCompareEx):
    pass

def log(*args):
    print(">> ", *args)


def run(command_list, *args, **kwargs):
    return check_output(command_list, *args, **kwargs).decode()


def get_json_from_process(command_list, *args, **kwargs):
    return loads(run(command_list, *args,**kwargs))


def check_len(item1, item2):
    if len(item1) == len(item2):
        return True
    log(f"SIZE DIFFERENCE: old={len(item1)}, new={len(item2)}")
    return False


def _exclude_pattern_matching(item, pattern_list):
    for pattern in pattern_list:
        if re.search(pattern, item):
            return True
    return False


def compare(old_data, new_data, exclude_pattern_list):
    if type(old_data) != type(new_data):
        raise NotComparable(old_data, new_data)
    check_len(old_data, new_data)
    if isinstance(new_data, (list, set, tuple)):
        _compare_list(old_data, new_data, exclude_pattern_list)
    elif isinstance(new_data, dict):
        _compare_dict(old_data, new_data, exclude_pattern_list)
    elif isinstance(new_data,str):
        _compare_string(old_data, new_data, exclude_pattern_list)
    elif isinstance(new_data, numbers.Number):
        _compare_string(old_data, new_data, exclude_pattern_list)


def _compare_list(old_data, new_data, exclude_pattern_list):
    min_items = old_data if len(old_data) <= len(new_data) else new_data
    for counter in range(len(min_items)):
        compare(old_data[counter], new_data[counter], exclude_pattern_list)
    if len(old_data) < len(new_data):
        for item in new_data[min_items:]:
            if not _exclude_pattern_matching(item, exclude_pattern_list):
                log("ADDED LIST ITEM: ", item)
    elif len(old_data) > len(new_data):
        for item in old_data[min_items:]:
            if not _exclude_pattern_matching(item, exclude_pattern_list):
                log("REMOVED LIST ITEM: ", item)


def _compare_dict(old_data, new_data, exclude_pattern_list):
    for key in list(set(old_data.keys() + new_data.keys())):
        if _exclude_pattern_matching(key, exclude_pattern_list):
            continue
        if key in old_data.keys() and key in new_data.keys():
            compare(old_data(key), new_data(key), exclude_pattern_list)
        elif key in old_data.keys():
            log(f"REMOVED DICT ITEM: key:{key} ", old_data(key))
        else:
            log(f"ADDED DICT ITEM: key:{key} ", new_data(key))


def _compare_string(old_data, new_data, exclude_pattern_list):
    if old_data != new_data and\
            (_exclude_pattern_matching(old_data,exclude_pattern_list) or
             _exclude_pattern_matching(new_data, exclude_pattern_list)):
        log(f"CHANGED STRING: {old_data} != {new_data}")


def _compare_num(old_data, new_data, exclude_pattern_list):
    if old_data != new_data:
        log(f"CHANGED NUMBER: {old_data} != {new_data}")