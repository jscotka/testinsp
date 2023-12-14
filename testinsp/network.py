from .base import TestInspector, JSON
from .utils import get_json_from_process, Comparator


class Interfaces(TestInspector):
    store_type = JSON
    _get_data_command_list = "ip -j a".split(" ")

    def get_data(self):
        return get_json_from_process(self._get_data_command_list)

    def check(self):
        result_list = Comparator().compare(self.data, self.get_data(), self.exclude_list)
        return result_list
