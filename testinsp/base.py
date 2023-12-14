from pathlib import Path
from json import loads, JSONDecodeError, dumps
from yaml import safe_load, YAMLError, safe_dump
from utils import FirstRunError

YAML = "yaml"
JSON = "json"
PLAIN = "plain"


class TestInspector:
    store_type = None

    def __init__(self, filename=None, pathname="/var/tmp/"):
        self.data = dict()
        self.exclude_list = list()
        self._default_filename = f"{self.__class__.__name__}.data"
        if filename is None:
            filename = self._default_filename
        self.storage_file = Path(pathname) / filename

    def get_data(self):
        raise NotImplementedError()

    def init(self):
        # try to load data, if data does not exist create first run
        try:
            self.load_explicit()
        except FirstRunError:
            self.data = self.get_data()

    def check(self):
        raise NotImplementedError()

    def load_guess(self):
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

    def load_explicit(self):
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

    def store(self):
        with open(self.storage_file, "w") as fd:
            if self.store_type == JSON:
                data = dumps(self.data)
            elif self.store_type == YAML:
                data = safe_dump(self.data)
            elif self.store_type == PLAIN:
                data = self.data
            fd.write(data)
