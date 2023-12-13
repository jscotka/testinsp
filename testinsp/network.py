from .base import TestInspector, JSON
from .utils import get_json_from_process, compare


class Interfaces(TestInspector):
    store_type = JSON
    _get_data_command_list = "ip -j a".split(" ")

    def init(self):
        self.data_storage = get_json_from_process(self._get_data_command_list)

    def check(self):
        new_state = get_json_from_process(self._get_data_command_list)
        compare()
