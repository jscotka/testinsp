from testinsp.network import NetworkInterfaces, FirewallStatus
from testinsp.storage import DiskInfo
from testinsp.etc import ListEtcDir
from testinsp.cockpit_config_files import CockpitPAM, CockpitConf
from testinsp.services import ServiceInfo
from testinsp.users import UserInfo, GroupInfo


class RunChecks:
    def __init__(self, external_executor=None, exclude_dict: dict = None):
        all_class = [
            NetworkInterfaces,
            DiskInfo,
            ListEtcDir,
            CockpitConf,
            CockpitPAM,
            ServiceInfo,
            FirewallStatus,
            UserInfo,
            GroupInfo,
        ]
        self.all = list()
        if not exclude_dict:
            exclude_dict = dict()
        for one_class in all_class:
            exclude_item_list = exclude_dict.get(one_class.__name__)
            item = one_class(
                external_executor=external_executor, exclude_list=exclude_item_list
            )
            self.all.append(item)

    def init(self):
        for item in self.all:
            item.init()

    def load(self):
        for item in self.all:
            item.load()

    def store(self):
        for item in self.all:
            item.store()

    def check(self):
        results = dict()
        for item in self.all:
            results[item.module_name] = item.check()
        return results
