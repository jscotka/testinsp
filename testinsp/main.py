from testinsp.network import NetworkInterfaces, FirewallStatus
from testinsp.storage import DiskInfo
from testinsp.etc import ListEtcDir
from testinsp.cockpit_config_files import CockpitPAM, CockpitConf
from testinsp.services import ServiceInfo



class RunChecks:
    all = [NetworkInterfaces(), DiskInfo(), ListEtcDir(), CockpitConf(), CockpitPAM(), ServiceInfo(), FirewallStatus()]

    def __init__(self):
        pass

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
            results[item. module_name] = item.check()
        return results
