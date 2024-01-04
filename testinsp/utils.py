import re
import os
import numbers
import difflib
from pathlib import Path
import shutil
from logging import getLogger
from testinsp.constants import (
    STORE_PATH,
    ADD,
    REM,
    CHANGE,
    CHANGE_TYPE,
    DATA_CHANGE,
    DATA_PATH,
)


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


class Comparator:
    tmp_files_comparator_path = f"{STORE_PATH}/file_comparator"

    def __init__(self, module_name, exclude_pattern_list):
        self.differences = list()
        self.module_name = module_name
        self.exclude_pattern_list = exclude_pattern_list
        self.logger = getLogger(self.module_name)

    def log(self, change_type, *args, internal_path=None):
        self.differences.append(
            {CHANGE_TYPE: change_type, DATA_CHANGE: args, DATA_PATH: internal_path}
        )
        path = ""
        if internal_path and isinstance(internal_path, list):
            path = "(" + ".".join(map(str, internal_path)) + ")"
        self.logger.info(f">> {self.module_name} {path}>> {args}")

    def check_len(self, item1, item2):
        if isinstance(item1, numbers.Number) or isinstance(item1, numbers.Number):
            return item1 == item2
        elif item1 is None or item2 is None:
            return item1 == item2
        elif len(item1) == len(item2):
            return True
        self.log(CHANGE, "SIZE", f"old={len(item1)}, new={len(item2)}")
        return False

    def _exclude_pattern_matching(self, item):
        # exclude matching just in case it is string.
        if not isinstance(item, str):
            return False
        for pattern in self.exclude_pattern_list:
            if re.search(pattern, item):
                return True
        return False

    def compare(self, old_data, new_data, internal_path=None):
        if internal_path is None:
            internal_path = list()
        if type(old_data) != type(new_data):
            raise NotComparable(old_data, new_data)
        self.check_len(old_data, new_data)
        if isinstance(new_data, (list, set, tuple)):
            self._compare_list(old_data, new_data, internal_path=internal_path)
        elif isinstance(new_data, dict):
            self._compare_dict(old_data, new_data, internal_path=internal_path)
        elif isinstance(new_data, str):
            self._compare_string(old_data, new_data, internal_path=internal_path)
        elif isinstance(new_data, numbers.Number):
            self._compare_num(old_data, new_data, internal_path=internal_path)
        return self.differences

    def _compare_list(self, old_data, new_data, internal_path):
        min_items = old_data if len(old_data) <= len(new_data) else new_data
        for counter in range(len(min_items)):
            self.compare(
                old_data[counter],
                new_data[counter],
                internal_path=internal_path + [counter],
            )
        if len(old_data) < len(new_data):
            for item in new_data[len(min_items) :]:
                if not self._exclude_pattern_matching(item):
                    self.log(ADD, item, internal_path=internal_path)
        elif len(old_data) > len(new_data):
            for item in old_data[len(min_items) :]:
                if not self._exclude_pattern_matching(item):
                    self.log(REM, item, internal_path=internal_path)

    def _compare_dict(self, old_data, new_data, internal_path):
        for key in set(list(old_data.keys()) + list(new_data.keys())):
            if self._exclude_pattern_matching(key):
                continue
            if key in old_data.keys() and key in new_data.keys():
                self.compare(
                    old_data[key], new_data[key], internal_path=internal_path + [key]
                )
            elif key in old_data.keys():
                self.log(REM, f"key:{key} ", old_data[key], internal_path=internal_path)
            else:
                self.log(ADD, f"key:{key} ", new_data[key], internal_path=internal_path)

    def _compare_string(self, old_data, new_data, internal_path):
        if "\n" in old_data or "\n" in new_data:
            self.compare_multiline(old_data, new_data, internal_path=internal_path)
        if old_data != new_data and not (
            self._exclude_pattern_matching(old_data)
            or self._exclude_pattern_matching(new_data)
        ):
            self.log(CHANGE, old_data, new_data, internal_path=internal_path)

    def _compare_num(self, old_data, new_data, internal_path):
        if old_data != new_data:
            self.log(CHANGE, old_data, new_data, internal_path=internal_path)

    def compare_multiline(self, old_data, new_data, internal_path):
        old_list = list()
        new_list = list()
        # filter excluded patterns
        for line in old_data.strip().split("\n"):
            if not self._exclude_pattern_matching(line):
                old_list.append(line)
        for line in new_data.strip().split("\n"):
            if not self._exclude_pattern_matching(line):
                new_list.append(line)
        if old_data == new_data:
            return
        different = difflib.ndiff(old_list, new_list)
        for item in different:
            line = item[2:]
            if item.startswith("+"):
                self.log(ADD, line, internal_path=internal_path)
            elif item.startswith("-"):
                self.log(REM, line, internal_path=internal_path)

    def __compare_files(self, file_path, name_to_store="", old_data=None):
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
        return self.compare_multiline(old_data, new_data)

    def __get_path_list(self, dir_path: Path) -> list:
        output = list()
        for item in dir_path.rglob("*"):
            clean_item = str(item)
            if not self._exclude_pattern_matching(clean_item):
                output.append(clean_item)
        return output

    def __compare_dir_ls(self, dir_name, name_to_store="", old_data=None):
        dir_path = Path(dir_name)
        sep = "\n"
        basename = dir_path.name
        name = name_to_store or basename
        storage_file = Path(self.tmp_files_comparator_path) / name
        if not old_data:
            os.makedirs(Path(self.tmp_files_comparator_path), exist_ok=True)
            if not storage_file.exists():
                with open(storage_file, "w") as fd:
                    data = sep.join(self.__get_path_list(dir_path))
                    fd.write(data)
                return data
            with open(storage_file, "r") as fd:
                old_data = set(fd.read().split(sep))
        new_data = set(self.__get_path_list(dir_path))
        removed = old_data - new_data
        added = old_data - new_data
        for item in removed:
            self.log(ADD, "FILE", item)
        for item in added:
            self.log(REM, "FILE", item)
        return self.differences
