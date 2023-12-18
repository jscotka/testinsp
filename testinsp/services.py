from testinsp.base import TestInspector
from testinsp.constants import PLAIN
from testinsp.utils import run


class ServiceInfo(TestInspector):
    store_type = PLAIN
    _get_data_command = "systemctl --type=service --state=running"

    def get_data(self):
        raw_data = run(self._get_data_command).splitlines()
        removed_header_footer = [item.strip() for item in raw_data[1:-5]]
        removed_header_footer.sort()
        data = "\n".join(removed_header_footer)
        return data
