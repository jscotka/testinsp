from testinsp.base import TestInspector
from testinsp.constants import YAML


class ListEtcDir(TestInspector):
    store_type = YAML
    dir_name = "/etc"

    def get_data(self):
        return self._get_dir_list_with_size(self.dir_name)
