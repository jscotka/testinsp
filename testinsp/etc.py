from testinsp.base import TestInspector
from testinsp.constants import YAML, STORE_PATH


class ListEtcDir(TestInspector):
    store_type = YAML
    dir_name = "/etc"
    # common backup files
    __static_exclude_list = ["[-~]$"]

    def __init__(
        self,
        filename=None,
        pathname=STORE_PATH,
        external_executor=None,
        exclude_list: list = None,
    ):
        super().__init__(
            filename=filename,
            pathname=pathname,
            external_executor=external_executor,
            exclude_list=exclude_list,
        )
        self.exclude_list += self.__static_exclude_list

    def get_data(self):
        return self._get_dir_list_with_size(self.dir_name)
