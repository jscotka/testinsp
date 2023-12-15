from testinsp.base import TestInspector
from testinsp.constants import JSON
from testinsp.utils import get_json_from_process


class NetworkInterfaces(TestInspector):
    store_type = JSON
    _get_data_command = "ip -j a"

    def __init__(self):
        super().__init__()
        self.exclude_list += ["preferred_life_time", "valid_life_time"]

    def get_data(self):
        return get_json_from_process(self._get_data_command)

