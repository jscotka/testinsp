from unittest import TestCase
from os import putenv, unsetenv, makedirs
from shutil import rmtree
from pprint import pprint
from subprocess import check_call
from testinsp.main import RunChecks


data = """[Session]
IdleTimeout=15
"""


class SuperTest(TestCase):
    def setUp(self) -> None:
        self.check = RunChecks()
        self.check.init()
        makedirs("cockpit", exist_ok=True)
        with open("cockpit/cockpit.conf", "w") as fd:
            fd.write(data)

    def testPass(self):
        pass

    def test_fail_conf1(self):
        putenv("XDG_CONFIG_DIRS", "/var:.")

    def test_fail_conf2(self):
        putenv("XDG_CONFIG_DIRS", "/var:.")
        self.check.init()
        data = """[Session]
IdleTimeout=30
"""
        with open("cockpit/cockpit.conf", "w") as fd:
            fd.write(data)

    def test_fail_etc(self):
        check_call("sudo touch /etc/cockpit/test.xx", shell=True)

    def tearDown(self) -> None:
        pprint(self.check.check())
        unsetenv("XDG_CONFIG_DIRS")
        rmtree("cockpit")
        check_call("sudo rm /etc/cockpit/test.xx 2>/dev/null || true", shell=True)
