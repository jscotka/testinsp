from yaml import safe_load
from testinsp.base import TestInspector
from testinsp.constants import YAML, STORE_PATH


class DiskInfo(TestInspector):
    store_type = YAML
    _get_data_command = "udisksctl dump"
    __static_exclude_list = ["^(?!/org/freedesktop/UDisks2/block_devices|\\.).*"]

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
        yaml_data = safe_load(
            self.run(self._get_data_command).replace("(", "[").replace(")", "]")
        )
        return yaml_data
