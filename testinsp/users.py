from testinsp.base import TestInspector
from testinsp.constants import YAML


class UserInfo(TestInspector):
    store_type = YAML
    _get_data_command = "getent passwd"

    def get_data(self):
        raw = self.run(self._get_data_command).strip()
        output = dict()
        for line in raw.splitlines():
            username, rest = line.split(":", 1)
            output[username] = rest
        return output


class GroupInfo(UserInfo):
    _get_data_command = "getent group"
