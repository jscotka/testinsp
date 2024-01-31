from unittest import TestCase
from pprint import pprint
from testinsp.network import NetworkInterfaces


class Network(TestCase):
    def test_network(self):
        interfaces = NetworkInterfaces()
        interfaces.init()
        pprint(interfaces.data)
