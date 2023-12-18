from testinsp.base import TestInspector
from testinsp.constants import YAML
from testinsp.utils import run, get_json_from_process


class NetworkInterfaces(TestInspector):
    store_type = YAML
    _get_data_command = "ip -j a"

    def __init__(self):
        super().__init__()
        self.exclude_list += ["preferred_life_time", "valid_life_time"]

    def get_data(self):
        return get_json_from_process(self._get_data_command)


class FirewallStatus(TestInspector):
    store_type = YAML
    _get_data_command = "firewall-cmd --list-all"

    def get_data(self):
        raw_data = run(self._get_data_command)
        data = dict()
        key = "Unknown"
        for raw_item in raw_data.splitlines():
            if not raw_item.startswith(" "):
                key = raw_item.strip()
                data[key] = dict()
                continue
            inner_key, value = raw_item.strip().split(":", 1)
            data[key][inner_key.strip()] = value.strip()
        return data
