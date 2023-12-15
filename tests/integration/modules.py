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

    def test_fail_new_network_iface(self):
        command="""sudo ip link add dev vm1 type veth peer name vm2;
            sudo ip link set dev vm1 up;
            sudo ip tuntap add tapm mode tap;
            sudo ip link set dev tapm up;
            sudo ip link add brm type bridge;
            sudo ip link set tapm master brm;
            sudo ip link set vm1 master brm;
            sudo ip addr add 10.0.0.1/32 dev brm;
            sudo ip addr add 10.0.0.2/32 dev vm2;
        """
        check_call(command, shell=True)

    def tearDown(self) -> None:
        pprint(self.check.check())
        unsetenv("XDG_CONFIG_DIRS")
        rmtree("cockpit")
        check_call("sudo rm /etc/cockpit/test.xx 2>/dev/null || true", shell=True)
        network_cmd_clean = """sudo ip addr del 10.0.0.2/32 dev vm2 || true;
        sudo ip addr del 10.0.0.1/32 dev brm 2>/dev/null|| true;
        sudo ip link set dev tapm down 2>/dev/null|| true;
        sudo ip link del brm type bridge 2>/dev/null|| true;
        sudo ip link set dev tapm down 2>/dev/null|| true;
        sudo ip tuntap del tapm mode tap 2>/dev/null|| true;
        sudo ip link set dev vm1 down 2>/dev/null|| true;
        sudo ip link del dev vm1 type veth peer name vm2 2>/dev/null|| true
        """
        check_call(network_cmd_clean, shell=True)
