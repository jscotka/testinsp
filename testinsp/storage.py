from yaml import safe_load
from .base import TestInspector
from .constants import YAML
from .utils import run


class DiskInfo(TestInspector):
    store_type = YAML
    _get_data_command = "udisksctl dump"

    def get_data(self):
        yaml_data = safe_load(run(self._get_data_command).replace("(", "[").replace(")", "]"))
        return yaml_data
