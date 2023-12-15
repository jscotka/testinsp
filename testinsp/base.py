import os
from pathlib import Path
from json import loads, JSONDecodeError, dumps
from yaml import safe_load, YAMLError, safe_dump

from .utils import FirstRunError, Comparator
from .constants import YAML, PLAIN, JSON, STORE_PATH


class TestInspector:
    store_type = None

    def __init__(self, filename=None, pathname=STORE_PATH):
        self.data = dict()
        self.exclude_list = list()
        class_name = self.__class__.__name__
        self.module_name = filename or class_name
        self._default_filename = f"{class_name}.data"
        os.makedirs(pathname, exist_ok=True)
        if filename is None:
            filename = self._default_filename
        self.storage_file = Path(pathname) / filename

    def get_data(self):
        raise NotImplementedError()

    def init(self):
        self.data = self.get_data()
        self._store()

    def check(self):
        new_data = self.get_data()
        comp = Comparator(self.module_name, self.exclude_list)
        result_list = comp.compare(self.data, self.get_data())
        self.data = new_data
        self._store()
        return result_list

    def _load_guess(self):
        with open(self.storage_file, "w") as fd:
            data_read = fd.read()
        try:
            self.data = loads(data_read)
            self.store_type = JSON
        except JSONDecodeError:
            try:
                self.data = safe_load(data_read)
                self.store_type = YAML
            except YAMLError:
                self.data = data_read
                self.store_type = PLAIN

    def _load_explicit(self):
        try:
            with open(self.storage_file, "r") as fd:
                data = fd.read()
        except FileNotFoundError:
            raise FirstRunError()
        if self.store_type == JSON:
            self.data = loads(data)
        elif self.store_type == YAML:
            self.data = safe_load(data)
        elif self.store_type == PLAIN:
            self.data = data

    def _store(self):
        with open(self.storage_file, "w") as fd:
            if self.store_type == JSON:
                data = dumps(self.data)
            elif self.store_type == YAML:
                data = safe_dump(self.data)
            elif self.store_type == PLAIN:
                data = self.data
            fd.write(data)
