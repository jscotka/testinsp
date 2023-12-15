from testinsp.base import TestInspector
from testinsp.utils import get_dir_list_with_size
from testinsp.constants import PLAIN


class ListEtcDir(TestInspector):
    store_type = PLAIN
    dir_name = "/etc"

    def get_data(self):
        return get_dir_list_with_size(self.dir_name)

