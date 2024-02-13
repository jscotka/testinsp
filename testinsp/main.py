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

    def check(self):
        results = dict()
        for item in self.all:
            results[item.module_name] = item.check()
        return results


class RunChecksInParallel(RunChecks):
    @staticmethod
    def _mp_helper(param):
        class_item = param[0]
        method = param[1]
        return (class_item, getattr(class_item, method)())

    def init(self):
        with Pool(len(self.all)) as process:
            output = process.map(self._mp_helper, [(x, "init") for x in self.all])
            self.all = [x[0] for x in output]

    def check(self):
        results = dict()
        with Pool(len(self.all)) as process:
            output = process.map(self._mp_helper, [(x, "check") for x in self.all])
        for counter in range(len(self.all)):
            results[self.all[counter].module_name] = output[counter][1]
        return results
