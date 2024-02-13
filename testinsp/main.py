from multiprocessing import Pool
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

    def check(self, init_after_check=False):
        results = dict()
        for item in self.all:
            results[item.module_name] = item.check(init_after_check=init_after_check)
        return results


class RunChecksInParallel(RunChecks):
    @staticmethod
    def _init_helper(class_item):
        class_item.init()
        return class_item

    @staticmethod
    def _check_helper(params):
        class_item = params[0]
        init_after_check = params[1]
        result = class_item.check(init_after_check=init_after_check)
        return class_item, result

    def init(self):
        with Pool(len(self.all)) as process:
            self.all = process.map(self._init_helper, self.all)

    def check(self, init_after_check=False):
        results = dict()
        with Pool(len(self.all)) as process:
            output = process.map(
                self._check_helper, [(x, init_after_check) for x in self.all]
            )
        for item in output:
            results[item[0].module_name] = item[1]
        if init_after_check:
            self.all = [x[0] for x in output]
        return results
