from multiprocessing import Process, Manager
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
    def __init__(self, external_executor=None, exclude_dict: dict = None):
        super().__init__(external_executor=external_executor, exclude_dict=exclude_dict)
        self.process_manager = Manager()
        __all = self.process_manager.list()
        for item in self.all:
            __all.append(item)
        self.all = __all

    @staticmethod
    def _init_helper(class_item):
        class_item.init()
        return class_item

    @staticmethod
    def _check_helper(class_item, init_after_check, result_dict):
        result = class_item.check(init_after_check=init_after_check)
        result_dict[class_item.module_name] = result

    def init(self):
        processes = list()
        for item in self.all:
            proc = Process(target=self._init_helper, args=(item,))
            proc.start()
            processes.append(proc)
        for item in processes:
            item.join()

    def check(self, init_after_check=False):
        results = self.process_manager.dict()
        processes = list()
        for item in self.all:
            proc = Process(
                target=self._check_helper, args=(item, init_after_check, results)
            )
            proc.start()
            processes.append(proc)
        for item in processes:
            item.join()
        return results
