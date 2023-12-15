from .network import NetworkInterfaces
from .storage import DiskInfo
from .etc import ListEtcDir
from .cockpit_config_files import CockpitPAM, CockpitConf



class RunChecks:
    all = [NetworkInterfaces(), DiskInfo(), ListEtcDir(), CockpitConf(), CockpitPAM()]

    def __init__(self):
        pass

    def init(self):
        for item in self.all:
            item.init()

    def check(self):
        results = dict()
        for item in self.all:
            results[item. module_name] = item.check()
        return results
