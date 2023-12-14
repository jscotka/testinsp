from subprocess import check_output
from json import loads
import re
import os
import numbers
import difflib
from pathlib import Path
import shutil


class GenericCompareEx(Exception):
    pass


class NotComparable(GenericCompareEx):
    pass


class ItemDifference(GenericCompareEx):
    pass


class DifferentSize(GenericCompareEx):
    pass


class FirstRunError(Exception):
    pass


def run(command_list, *args, **kwargs):
    return check_output(command_list, *args, **kwargs).decode()


def get_json_from_process(command_list, *args, **kwargs):
    return loads(run(command_list, *args, **kwargs))


class Comparator:
    tmp_files_comparator_path = "/var/tmp/testinsp/file_comparator"

    def __init__(self):
        self.differences = list()

    def log(self, *args):
        self.differences += args
        print(">> ", *args)

    def check_len(self, item1, item2):
        if len(item1) == len(item2):
            return True
        self.log(f"SIZE DIFFERENCE: old={len(item1)}, new={len(item2)}")
        return False

    @staticmethod
    def _exclude_pattern_matching(item, pattern_list):
        for pattern in pattern_list:
            if re.search(pattern, item):
                return True
        return False

    def compare(self, old_data, new_data, exclude_pattern_list):
        if type(old_data) != type(new_data):
            raise NotComparable(old_data, new_data)
        self.check_len(old_data, new_data)
        if isinstance(new_data, (list, set, tuple)):
            self._compare_list(old_data, new_data, exclude_pattern_list)
        elif isinstance(new_data, dict):
            self._compare_dict(old_data, new_data, exclude_pattern_list)
        elif isinstance(new_data, str):
            self._compare_string(old_data, new_data, exclude_pattern_list)
        elif isinstance(new_data, numbers.Number):
            self._compare_string(old_data, new_data, exclude_pattern_list)
        return self.differences

    def _compare_list(self, old_data, new_data, exclude_pattern_list):
        min_items = old_data if len(old_data) <= len(new_data) else new_data
        for counter in range(len(min_items)):
            self.compare(old_data[counter], new_data[counter], exclude_pattern_list)
        if len(old_data) < len(new_data):
            for item in new_data[min_items:]:
                if not self._exclude_pattern_matching(item, exclude_pattern_list):
                    self.log("ADDED LIST ITEM: ", item)
        elif len(old_data) > len(new_data):
            for item in old_data[min_items:]:
                if not self._exclude_pattern_matching(item, exclude_pattern_list):
                    self.log("REMOVED LIST ITEM: ", item)

    def _compare_dict(self, old_data, new_data, exclude_pattern_list):
        for key in list(set(old_data.keys() + new_data.keys())):
            if self._exclude_pattern_matching(key, exclude_pattern_list):
                continue
            if key in old_data.keys() and key in new_data.keys():
                self.compare(old_data(key), new_data(key), exclude_pattern_list)
            elif key in old_data.keys():
                self.log(f"REMOVED DICT ITEM: key:{key} ", old_data(key))
            else:
                self.log(f"ADDED DICT ITEM: key:{key} ", new_data(key))

    def _compare_string(self, old_data, new_data, exclude_pattern_list):
        if "\n" in old_data:
            return self.compare_multiline(old_data, new_data, exclude_pattern_list)
        if old_data != new_data and not\
                (self._exclude_pattern_matching(old_data, exclude_pattern_list) or
                 self._exclude_pattern_matching(new_data, exclude_pattern_list)):
            self.log(f"CHANGED STRING: {old_data} != {new_data}")

    def _compare_num(self, old_data, new_data, exclude_pattern_list):
        if old_data != new_data:
            self.log(f"CHANGED NUMBER: {old_data} != {new_data}")

    def compare_multiline(self, old_data, new_data, exclude_pattern_list):
        old_list = list()
        new_list = list()
        # filter excluded patterns
        for line in old_data.strip().split("\n"):
            if not self._exclude_pattern_matching(line, exclude_pattern_list):
                old_list.append(line)
        for line in new_data.strip().split("\n"):
            if not self._exclude_pattern_matching(line, exclude_pattern_list):
                new_list.append(line)
        if old_data == new_data:
            return
        different = difflib.ndiff(old_list, new_list)
        for item in different:
            line = item[2:]
            if item.startswith("+"):
                self.log("ADDED LINE", f">{line}<")
            elif item.startswith("-"):
                self.log("REMOVED LINE", f">{line}<")
        return self.differences

    def compare_files(self, file_path, exclude_pattern_list, name_to_store="", old_data=None):
        file = Path(file_path)
        basename = file.name
        name = name_to_store or basename
        storage_file = Path(self.tmp_files_comparator_path) / name
        if not old_data:
            os.makedirs(Path(self.tmp_files_comparator_path), exist_ok=True)
            if not storage_file.exists():
                shutil.copy(file, storage_file, follow_symlinks=True)
                with open(file, "r") as fd:
                    data = fd.read()
                return data
            with open(storage_file, "r") as fd:
                old_data = fd.read()
        with open(file, "r") as fd:
            new_data = fd.read()
            shutil.copy(file, storage_file, follow_symlinks=True)
        return self.compare_multiline(old_data, new_data, exclude_pattern_list)

    def __get_path_list(self, dir_path: Path, exclude_pattern_list) -> list:
        output = list()
        for item in dir_path.rglob("*"):
            clean_item = str(item)
            if not self._exclude_pattern_matching(clean_item, exclude_pattern_list):
                output.append(clean_item)
        return output

    def compare_dir_ls(self, dir_name, exclude_pattern_list, name_to_store="", old_data=None):
        dir_path = Path(dir_name)
        sep = "\n"
        basename = dir_path.name
        name = name_to_store or basename
        storage_file = Path(self.tmp_files_comparator_path) / name
        if not old_data:
            os.makedirs(Path(self.tmp_files_comparator_path), exist_ok=True)
            if not storage_file.exists():
                with open(storage_file, "w") as fd:
                    data = sep.join(self.__get_path_list(dir_path, exclude_pattern_list))
                    fd.write(data)
                return data
            with open(storage_file, "r") as fd:
                old_data = set(fd.read().split(sep))
        new_data = set(self.__get_path_list(dir_path, exclude_pattern_list))
        removed = old_data - new_data
        added = old_data - new_data
        for item in removed:
            self.log("REMOVED FILE", item)
        for item in added:
            self.log("ADDED FILE", item)
        return self.differences
